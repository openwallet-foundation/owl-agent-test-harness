using System.Collections.Generic;
using System.Threading.Tasks;
using Hyperledger.Aries.Agents;
using Hyperledger.Aries;
using DotNet.Backchannel.Messages;
using DotNet.Backchannel.Models;
using Microsoft.Extensions.Caching.Memory;
using Hyperledger.Aries.Decorators.Threading;

namespace DotNet.Backchannel.Handlers
{
    internal class PresentationAckHandler : IMessageHandler
    {
        private IMemoryCache _proofCache;

        /// <summary>Initializes a new instance of the <see cref="PresentationAckHandler"/> class.</summary>
        /// <param name="memoryCache">The memory cache</param>
        public PresentationAckHandler(
            IMemoryCache memoryCache)
        {
            _proofCache = memoryCache;
        }

        /// <summary>
        /// Gets the supported message types.
        /// </summary>
        /// <value>
        /// The supported message types.
        /// </value>
        public IEnumerable<MessageType> SupportedMessageTypes => new MessageType[]
        {
           CustomMessageTypes.AckPresentation,
           CustomMessageTypes.AckPresentationHttps
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
                case CustomMessageTypes.AckPresentation:
                case CustomMessageTypes.AckPresentationHttps:
                    {
                        var presentationAck = messageContext.GetMessage<AckPresentationMessage>();

                        var threadId = presentationAck.GetThreadId();
                        var THPresentationExchange = _proofCache.Get<TestHarnessPresentationExchange>(threadId);

                        if (presentationAck.Status == "OK" && THPresentationExchange.State == TestHarnessPresentationExchangeState.PresentationSent)
                        {
                            THPresentationExchange.State = TestHarnessPresentationExchangeState.Done;
                        }

                        break;
                    }
                default:
                    throw new AriesFrameworkException(ErrorCode.InvalidMessage,
                        $"Unsupported message type {messageContext.GetMessageType()}");
            }

            return null;
        }
    }
}