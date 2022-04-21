using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Hyperledger.Aries.Agents;
using Hyperledger.Aries.Extensions;
using Hyperledger.Aries.Storage;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Hyperledger.Aries.Features.IssueCredential;
using Hyperledger.Aries;
using DotNet.Backchannel.Messages;
using DotNet.Backchannel.Models;
using Microsoft.Extensions.Caching.Memory;
using Hyperledger.Aries.Contracts;
using Hyperledger.Aries.Utils;
using Hyperledger.Aries.Decorators.Threading;
using Hyperledger.Aries.Models.Events;
using Hyperledger.Aries.Features.Handshakes.DidExchange;
using Hyperledger.Aries.Features.Handshakes.Common;

namespace DotNet.Backchannel.Handlers
{
    // Because the framework doesn't handle credential propose message, and also needs a custom implementation for the credential offer
    // for now we override the credential handler.
    internal class AATHCredentialHandler : IMessageHandler
    {
        private readonly IEventAggregator _eventAggregator;
        private readonly ICredentialService _credentialService;
        private readonly IWalletRecordService _recordService;
        private readonly IMessageService _messageService;
        private IMemoryCache _credentialCache;

        /// <summary>Initializes a new instance of the <see cref="DefaultCredentialHandler"/> class.</summary>
        /// <param name="eventAggregator">The event aggregator.</param>
        /// <param name="credentialService">The credential service.</param>
        /// <param name="recordService">The wallet record service.</param>
        /// <param name="messageService">The message service.</param>
        /// <param name="memoryCache">The memory cache</param>
        public AATHCredentialHandler(
            IEventAggregator eventAggregator,
            ICredentialService credentialService,
            IWalletRecordService recordService,
            IMessageService messageService,
            IMemoryCache memoryCache)
        {
            _eventAggregator = eventAggregator;
            _credentialService = credentialService;
            _recordService = recordService;
            _messageService = messageService;
            _credentialCache = memoryCache;
        }

        /// <summary>
        /// Gets the supported message types.
        /// </summary>
        /// <value>
        /// The supported message types.
        /// </value>
        public IEnumerable<MessageType> SupportedMessageTypes => new MessageType[]
        {
            MessageTypes.IssueCredentialNames.ProposeCredential,
            MessageTypes.IssueCredentialNames.OfferCredential,
            MessageTypes.IssueCredentialNames.RequestCredential,
            MessageTypes.IssueCredentialNames.IssueCredential,
            MessageTypesHttps.IssueCredentialNames.ProposeCredential,
            MessageTypesHttps.IssueCredentialNames.OfferCredential,
            MessageTypesHttps.IssueCredentialNames.RequestCredential,
            MessageTypesHttps.IssueCredentialNames.IssueCredential,

        };

        /// <summary>
        /// Processes the agent message
        /// </summary>
        /// <param name="agentContext"></param>
        /// <param name="messageContext">The agent message.</param>
        /// <returns></returns>
        /// <exception cref="AriesFrameworkException">Unsupported message type {messageType}</exception>
        public async Task<AgentMessage> ProcessAsync(IAgentContext agentContext, UnpackedMessageContext messageContext)
        {
            switch (messageContext.GetMessageType())
            {
                case MessageTypes.IssueCredentialNames.ProposeCredential:
                case MessageTypesHttps.IssueCredentialNames.ProposeCredential:
                    {
                        var credentialProposal = messageContext.GetMessage<CustomCredentialProposeMessage>();

                        CredentialRecord credentialRecord;
                        TestHarnessCredentialExchange THCredentialExchange;
                        try
                        {
                            // Credential can be proposed for an existing exchange
                            // so we must first check if the message contains 
                            THCredentialExchange = _credentialCache.Get<TestHarnessCredentialExchange>(credentialProposal.GetThreadId());
                            credentialRecord = await _credentialService.GetByThreadIdAsync(agentContext, THCredentialExchange.ThreadId);

                            // check if the proposal came from the same connection
                            if (messageContext.Connection?.Id != credentialRecord.ConnectionId)
                            {
                                throw new AriesFrameworkException(ErrorCode.RecordInInvalidState, "Connection from credential proposal is not same as previously stored record.");
                            }
                        }
                        catch
                        {
                            // Create new CredentialRecord if no existing credential record exists
                            credentialRecord = new CredentialRecord
                            {
                                Id = Guid.NewGuid().ToString(),
                                ConnectionId = messageContext.Connection?.Id,
                            };

                            credentialRecord.SetTag(TagConstants.Role, TagConstants.Issuer);
                            credentialRecord.SetTag(TagConstants.LastThreadId, credentialProposal.GetThreadId());

                            await _recordService.AddAsync(agentContext.Wallet, credentialRecord);

                            THCredentialExchange = new TestHarnessCredentialExchange
                            {
                                RecordId = credentialRecord.Id,
                                ThreadId = credentialProposal.GetThreadId(),
                                State = TestHarnessCredentialExchangeState.ProposalReceived,
                            };
                            _credentialCache.Set(THCredentialExchange.ThreadId, THCredentialExchange);
                        }

                        // Updates that should be applied both when the credential record already exists or not
                        credentialRecord.CredentialDefinitionId = credentialProposal.CredentialDefinitionId;
                        credentialRecord.SchemaId = credentialProposal.SchemaId;
                        credentialRecord.CredentialAttributesValues = credentialProposal.CredentialProposal?.Attributes
                                    .Select(x => new CredentialPreviewAttribute
                                    {
                                        Name = x.Name,
                                        MimeType = x.MimeType,
                                        Value = x.Value
                                    }).ToArray();
                        // State should be proposal-received
                        credentialRecord.State = CredentialState.Offered;

                        await _recordService.UpdateAsync(agentContext.Wallet, credentialRecord);

                        _eventAggregator.Publish(new ServiceMessageProcessingEvent
                        {
                            RecordId = credentialRecord.Id,
                            MessageType = credentialProposal.Type,
                            ThreadId = credentialProposal.GetThreadId()
                        });

                        messageContext.ContextRecord = credentialRecord;

                        return null;
                    }
                case MessageTypes.IssueCredentialNames.OfferCredential:
                case MessageTypesHttps.IssueCredentialNames.OfferCredential:
                    {
                        var offer = messageContext.GetMessage<CredentialOfferMessage>();
                        var recordId = await this.ProcessOfferAsync(
                            agentContext, offer, messageContext.Connection);

                        messageContext.ContextRecord = await _credentialService.GetAsync(agentContext, recordId);

                        return null;
                    }
                case MessageTypes.IssueCredentialNames.RequestCredential:
                case MessageTypesHttps.IssueCredentialNames.RequestCredential:
                    {
                        var request = messageContext.GetMessage<CredentialRequestMessage>();
                        var recordId = await _credentialService.ProcessCredentialRequestAsync(
                                agentContext: agentContext,
                                credentialRequest: request,
                                connection: messageContext.Connection);
                        if (request.ReturnRoutingRequested() && messageContext.Connection == null)
                        {
                            var (message, record) = await _credentialService.CreateCredentialAsync(agentContext, recordId);
                            messageContext.ContextRecord = record;
                            return message;
                        }
                        else
                        {
                            messageContext.ContextRecord = await _credentialService.GetAsync(agentContext, recordId);
                            return null;
                        }
                    }

                case MessageTypes.IssueCredentialNames.IssueCredential:
                case MessageTypesHttps.IssueCredentialNames.IssueCredential:
                    {
                        var credential = messageContext.GetMessage<CredentialIssueMessage>();
                        var recordId = await _credentialService.ProcessCredentialAsync(
                            agentContext, credential, messageContext.Connection);

                        messageContext.ContextRecord = await UpdateValuesAsync(
                            credentialId: recordId,
                            credentialIssue: messageContext.GetMessage<CredentialIssueMessage>(),
                            agentContext: agentContext);

                        return null;
                    }
                default:
                    throw new AriesFrameworkException(ErrorCode.InvalidMessage,
                        $"Unsupported message type {messageContext.GetMessageType()}");
            }
        }

        /// <summary>
        /// Process an offer, taking previous proposals into account. The framework doesn't fully
        /// support credential proposals, and I don't know how to override one service function
        /// so for now we just use a custom handler and this function.
        /// </summary>
        /// <param name="agentContext"></param>
        /// <param name="credentialOffer"></param>
        /// <param name="connection"></param>
        /// <returns></returns>
        private async Task<string> ProcessOfferAsync(IAgentContext agentContext, CredentialOfferMessage credentialOffer,
                 ConnectionRecord connection)
        {
            var offerAttachment = credentialOffer.Offers.FirstOrDefault(x => x.Id == "libindy-cred-offer-0")
                                  ?? throw new ArgumentNullException(nameof(CredentialOfferMessage.Offers));

            var offerJson = offerAttachment.Data.Base64.GetBytesFromBase64().GetUTF8String();
            var offer = JObject.Parse(offerJson);
            var definitionId = offer["cred_def_id"].ToObject<string>();
            var schemaId = offer["schema_id"].ToObject<string>();

            // check if credential already exists
            CredentialRecord credentialRecord;
            try
            {
                credentialRecord = await _credentialService.GetByThreadIdAsync(agentContext, credentialOffer.GetThreadId());

                if (credentialRecord.ConnectionId != connection.Id)
                {
                    throw new AriesFrameworkException(ErrorCode.InvalidRecordData, "Connection from credential offer is not same as previously stored record.");
                }
            }
            catch
            {
                // Write offer record to local wallet
                credentialRecord = new CredentialRecord
                {
                    Id = Guid.NewGuid().ToString(),
                    ConnectionId = connection?.Id,
                };
                credentialRecord.SetTag(TagConstants.Role, TagConstants.Holder);
                credentialRecord.SetTag(TagConstants.LastThreadId, credentialOffer.GetThreadId());

                await _recordService.AddAsync(agentContext.Wallet, credentialRecord);

                var THCredentialExchange = new TestHarnessCredentialExchange
                {
                    RecordId = credentialRecord.Id,
                    ThreadId = credentialOffer.GetThreadId(),
                    State = TestHarnessCredentialExchangeState.OfferReceived
                };

                _credentialCache.Set(THCredentialExchange.ThreadId, THCredentialExchange);
            }

            credentialRecord.OfferJson = offerJson;
            credentialRecord.CredentialDefinitionId = definitionId;
            credentialRecord.SchemaId = schemaId;
            credentialRecord.CredentialAttributesValues = credentialOffer.CredentialPreview?.Attributes
                .Select(x => new CredentialPreviewAttribute
                {
                    Name = x.Name,
                    MimeType = x.MimeType,
                    Value = x.Value
                }).ToArray();
            credentialRecord.State = CredentialState.Offered;

            await _recordService.UpdateAsync(agentContext.Wallet, credentialRecord);

            _eventAggregator.Publish(new ServiceMessageProcessingEvent
            {
                RecordId = credentialRecord.Id,
                MessageType = credentialOffer.Type,
                ThreadId = credentialOffer.GetThreadId()
            });

            return credentialRecord.Id;
        }

        private async Task<CredentialRecord> UpdateValuesAsync(string credentialId, CredentialIssueMessage credentialIssue, IAgentContext agentContext)
        {
            var credentialAttachment = credentialIssue.Credentials.FirstOrDefault(x => x.Id == "libindy-cred-0")
                ?? throw new ArgumentException("Credential attachment not found");

            var credentialJson = credentialAttachment.Data.Base64.GetBytesFromBase64().GetUTF8String();

            var jcred = JObject.Parse(credentialJson);
            var values = jcred["values"].ToObject<Dictionary<string, AttributeValue>>();

            var credential = await _credentialService.GetAsync(agentContext, credentialId);
            credential.CredentialAttributesValues = values.Select(x => new CredentialPreviewAttribute { Name = x.Key, Value = x.Value.Raw, MimeType = CredentialMimeTypes.TextMimeType }).ToList();
            await _recordService.UpdateAsync(agentContext.Wallet, credential);

            return credential;
        }

        private class AttributeValue
        {
            [JsonProperty("raw")]
            public string Raw { get; set; }

            [JsonProperty("encoded")]
            public string Encoded { get; set; }
        }
    }
}