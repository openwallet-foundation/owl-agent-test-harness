using System;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using DotNet.Backchannel.Models;
using Microsoft.Extensions.Caching.Memory;
using DotNet.Backchannel.Messages;

using Hyperledger.Aries.Features.IssueCredential;
using Hyperledger.Aries.Storage;
using Hyperledger.Aries.Agents;
using Hyperledger.Aries.Utils;
using Hyperledger.Aries.Features.DidExchange;
using Hyperledger.Aries.Models.Events;
using Hyperledger.Aries.Contracts;

using System.Reactive.Linq;
using Hyperledger.Aries.Configuration;
using Hyperledger.Indy.AnonCredsApi;
using Newtonsoft.Json.Linq;
using System.Linq;
using Hyperledger.Aries.Decorators.Attachments;
using Hyperledger.Aries.Extensions;
using Hyperledger.Aries.Decorators.Threading;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command/issue-credential")]
    [ApiController]
    public class IssueCredentialController : ControllerBase
    {
        private readonly ICredentialService _credentialService;
        private readonly IWalletRecordService _recordService;
        private readonly IEventAggregator _eventAggregator;
        private readonly IProvisioningService _provisionService;
        private readonly IConnectionService _connectionService;
        private readonly IAgentProvider _agentContextProvider;
        private readonly IMessageService _messageService;
        private IMemoryCache _credentialCache;

        public IssueCredentialController(
            ICredentialService credentialService,
            IWalletRecordService recordService,
            IEventAggregator eventAggregator,
            IProvisioningService provisionService,
            IConnectionService connectionService,
            IAgentProvider agentContextProvider,
            IMessageService messageService,
            IMemoryCache memoryCache
            )
        {
            _credentialService = credentialService;
            _recordService = recordService;
            _eventAggregator = eventAggregator;
            _provisionService = provisionService;
            _connectionService = connectionService;
            _agentContextProvider = agentContextProvider;
            _messageService = messageService;
            _credentialCache = memoryCache;
        }

        [HttpGet("{threadId}")]
        public async Task<IActionResult> GetCredentialRecordByThreadIdAsync([FromRoute] string threadId)
        {
            var context = await _agentContextProvider.GetContextAsync();

            try
            {
                var credentialRecord = await _credentialService.GetByThreadIdAsync(context, threadId);
                var THCredentialExchange = _credentialCache.Get<TestHarnessCredentialExchange>(threadId);
                if (THCredentialExchange == null) return NotFound();

                return Ok(THCredentialExchange);
            }
            catch
            {
                // Can't find the credential record
                return NotFound();
            }
        }

        [HttpPost("send-proposal")]
        public async Task<IActionResult> SendCredentialProposalAsync(OperationBody body)
        {
            var context = await _agentContextProvider.GetContextAsync();
            var proposal = body.Data;
            var connectionId = (string)proposal["connection_id"];
            var credentialPreview = proposal["credential_proposal"].ToObject<CustomCredentialPreviewMessage>();
            var credentialDefinitionId = (string)proposal["cred_def_id"];
            var schemaId = (string)proposal["schema_id"];
            var connection = await _connectionService.GetAsync(context, connectionId); // TODO: Handle AriesFrameworkException if connection not found

            var threadId = Guid.NewGuid().ToString();

            credentialPreview.Attributes = CleanCredentialPreviewAttributes(credentialPreview.Attributes);

            // TODO: add support for v1.1 wich includes 'schema_issuer_did', 'schema_name', 'schema_version', 'issuer_did'
            // TODO: should we support in response to previous message? Not possible with AATH atm I think.
            var credentialProposeMessage = new CustomCredentialProposeMessage
            {
                Id = threadId,
                Comment = (string)proposal["comment"] ?? "hello", // ACA-Py requires comment
                CredentialProposal = credentialPreview,
                CredentialDefinitionId = credentialDefinitionId,
                SchemaId = schemaId
            };

            var credentialRecord = new CredentialRecord
            {
                Id = Guid.NewGuid().ToString(),
                ConnectionId = connectionId,
                CredentialAttributesValues = credentialPreview.Attributes,
                CredentialDefinitionId = credentialDefinitionId,
                SchemaId = schemaId,
                // State should be proposal-received
                State = CredentialState.Offered
            };
            credentialRecord.SetTag(TagConstants.Role, TagConstants.Holder);
            credentialRecord.SetTag(TagConstants.LastThreadId, threadId);

            await _recordService.AddAsync(context.Wallet, credentialRecord);

            var THCredentialExchange = new TestHarnessCredentialExchange
            {
                RecordId = credentialRecord.Id,
                ThreadId = threadId,
                State = TestHarnessCredentialExchangeState.ProposalSent,
            };

            _credentialCache.Set(THCredentialExchange.ThreadId, THCredentialExchange);

            // Listen for credential offer to update the state
            UpdateStateOnMessage(THCredentialExchange, TestHarnessCredentialExchangeState.OfferReceived, _ => _.MessageType == MessageTypes.IssueCredentialNames.OfferCredential && _.ThreadId == THCredentialExchange.ThreadId);

            await _messageService.SendAsync(context.Wallet, credentialProposeMessage, connection);

            return Ok(THCredentialExchange);
        }

        [HttpPost("send-offer")]
        public async Task<IActionResult> SendCredentialOfferAsync(OperationBody body)
        {
            var context = await _agentContextProvider.GetContextAsync();
            var issuer = await _provisionService.GetProvisioningAsync(context.Wallet);
            var threadId = body.Id;

            await Task.Delay(5000);

            string connectionId;
            TestHarnessCredentialExchange THCredentialExchange;
            CredentialOfferMessage credentialOffer;
            CredentialRecord credentialRecord;

            // Send offer in response to proposal
            if (threadId != null)
            {
                THCredentialExchange = _credentialCache.Get<TestHarnessCredentialExchange>(threadId);

                credentialRecord = await _credentialService.GetAsync(context, THCredentialExchange.RecordId);
                connectionId = credentialRecord.ConnectionId;

                var offerJson = await AnonCreds.IssuerCreateCredentialOfferAsync(context.Wallet, credentialRecord.CredentialDefinitionId);
                var offerJobj = JObject.Parse(offerJson);
                var schemaId = offerJobj["schema_id"].ToObject<string>();

                // Update credential record
                credentialRecord.SchemaId = schemaId;
                credentialRecord.OfferJson = offerJson;
                credentialRecord.State = CredentialState.Offered;
                credentialRecord.SetTag(TagConstants.IssuerDid, issuer.IssuerDid);
                await _recordService.UpdateAsync(context.Wallet, credentialRecord);

                credentialOffer = new CredentialOfferMessage
                {
                    CredentialPreview = new CredentialPreviewMessage
                    {
                        Attributes = CleanCredentialPreviewAttributes(credentialRecord.CredentialAttributesValues.ToArray())
                    },
                    Comment = "credential-offer", // ACA-Py requires comment
                    Offers = new Attachment[]
                    {
                        new Attachment
                        {
                            Id = "libindy-cred-offer-0",
                            MimeType = CredentialMimeTypes.ApplicationJsonMimeType,
                            Data = new AttachmentContent
                            {
                                Base64 = offerJson.GetUTF8Bytes().ToBase64String()
                            }
                        }
                    }
                };

                credentialOffer.ThreadFrom(threadId);

                THCredentialExchange.State = TestHarnessCredentialExchangeState.OfferSent;
            }
            // Send Offer to start credential issuance flow
            else
            {
                var offer = body.Data;
                connectionId = (string)offer["connection_id"];
                var credentialPreview = offer["credential_preview"].ToObject<CustomCredentialPreviewMessage>();
                var credentialDefinitionId = (string)offer["cred_def_id"];

                credentialPreview.Attributes = CleanCredentialPreviewAttributes(credentialPreview.Attributes);

                (credentialOffer, credentialRecord) = await _credentialService.CreateOfferAsync(context, new OfferConfiguration
                {
                    CredentialAttributeValues = credentialPreview.Attributes,
                    CredentialDefinitionId = credentialDefinitionId,
                    IssuerDid = issuer.IssuerDid
                }, connectionId);

                THCredentialExchange = new TestHarnessCredentialExchange
                {
                    RecordId = credentialRecord.Id,
                    ThreadId = credentialRecord.GetTag(TagConstants.LastThreadId),
                    State = TestHarnessCredentialExchangeState.OfferSent
                };
                _credentialCache.Set(THCredentialExchange.ThreadId, THCredentialExchange);
            }

            var connection = await _connectionService.GetAsync(context, connectionId); // TODO: Handle AriesFrameworkException if connection not found

            // TODO: find better way to listen for changes. As the state can move to other statest than just RequestReceived
            // Listen for credential request to update the state
            UpdateStateOnMessage(THCredentialExchange, TestHarnessCredentialExchangeState.RequestReceived, _ => _.MessageType == MessageTypes.IssueCredentialNames.RequestCredential && _.ThreadId == THCredentialExchange.ThreadId);

            await _messageService.SendAsync(context.Wallet, credentialOffer, connection);

            return Ok(THCredentialExchange);
        }

        [HttpPost("send-request")]
        public async Task<IActionResult> SendCredentialRequestAsync(OperationBody body)
        {
            // Indy does not support startign from a credential-request. So the id is always the thread id
            var threadId = body.Id;
            var THCredentialExchange = _credentialCache.Get<TestHarnessCredentialExchange>(threadId);
            var context = await _agentContextProvider.GetContextAsync();

            var (credentialRequest, credentialRecord) = await _credentialService.CreateRequestAsync(context, THCredentialExchange.RecordId);
            THCredentialExchange.State = TestHarnessCredentialExchangeState.RequestSent;

            // TODO: find better way to listen for changes. As the state can move to other statest than just CredentialReceived
            // Listen for issue credential to update the state
            UpdateStateOnMessage(THCredentialExchange, TestHarnessCredentialExchangeState.CredentialReceived, _ => _.MessageType == MessageTypes.IssueCredentialNames.IssueCredential && _.ThreadId == THCredentialExchange.ThreadId);

            var connection = await _connectionService.GetAsync(context, credentialRecord.ConnectionId); // TODO: Handle AriesFrameworkException if connection not found
            await _messageService.SendAsync(context.Wallet, credentialRequest, connection);

            return Ok(THCredentialExchange);
        }

        [HttpPost("issue")]
        public async Task<IActionResult> IssueCredentialAsync(OperationBody body)
        {
            await Task.Delay(5000);

            var threadId = body.Id;
            var context = await _agentContextProvider.GetContextAsync();
            var THCredentialExchange = _credentialCache.Get<TestHarnessCredentialExchange>(threadId);

            // TODO: should we use body.Data? This can contain an optional comment.
            var (credentialIssueMessage, credentialRecord) = await _credentialService.CreateCredentialAsync(context, THCredentialExchange.RecordId);
            var connection = await _connectionService.GetAsync(context, credentialRecord.ConnectionId);

            await _messageService.SendAsync(context.Wallet, credentialIssueMessage, connection);

            THCredentialExchange.State = TestHarnessCredentialExchangeState.CredentialIssued;

            return Ok(THCredentialExchange);
        }

        [HttpPost("store")]
        public async Task<IActionResult> StoreCredentialAsync(OperationBody body)
        {
            var threadId = body.Id;
            var context = await _agentContextProvider.GetContextAsync();
            var THCredentialExchange = _credentialCache.Get<TestHarnessCredentialExchange>(threadId);
            var credentialRecord = _credentialService.GetAsync(context, THCredentialExchange.RecordId);

            // TODO: Should we do some checks here??
            THCredentialExchange.State = TestHarnessCredentialExchangeState.Done;

            return Ok(THCredentialExchange);
        }

        /// <summary>
        /// prevent mime type not supported error when mime type is null
        /// </summary>
        /// <param name="attributes"></param>
        /// <returns></returns>
        private CredentialPreviewAttribute[] CleanCredentialPreviewAttributes(CredentialPreviewAttribute[] attributes) => attributes.Select(x =>
            new CredentialPreviewAttribute
            {
                Name = x.Name,
                MimeType = x.MimeType == null ? CredentialMimeTypes.TextMimeType : x.MimeType,
                Value = x.Value?.ToString()
            }).ToArray();

        private void UpdateStateOnMessage(TestHarnessCredentialExchange testHarnessCredentialExchange, TestHarnessCredentialExchangeState nextState, Func<ServiceMessageProcessingEvent, bool> predicate)
        {
            System.Console.WriteLine($"Waiting to update state to ${nextState}, on credential {testHarnessCredentialExchange.ThreadId}, from state: {testHarnessCredentialExchange.State} ");
            _eventAggregator.GetEventByType<ServiceMessageProcessingEvent>()
            .Where(predicate)
            .Take(1)
            .Subscribe(_ => { System.Console.WriteLine($"Updated state to ${nextState}, on credential {testHarnessCredentialExchange.ThreadId}, from state: {testHarnessCredentialExchange.State} "); testHarnessCredentialExchange.State = nextState; });
        }
    }
}
