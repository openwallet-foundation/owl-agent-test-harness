using System.Threading.Tasks;
using Microsoft.Extensions.Caching.Memory;
using DotNet.Backchannel.Models;

using Hyperledger.Aries.Features.TrustPing;
using Hyperledger.Aries.Agents;

namespace DotNet.Backchannel.Middlewares
{
    public class MessageAgentMiddleware : IAgentMiddleware
    {
        private IMemoryCache _cache;
        public MessageAgentMiddleware(
            IMemoryCache memoryCache)
        {
            _cache = memoryCache;
        }

        /// <inheritdoc />
        public async Task OnMessageAsync(IAgentContext agentContext, UnpackedMessageContext messageContext)
        {
            // TrustPingMessage event aggregator event doesn't include the connection so we can't verify whether the
            // received trust ping comes from the connection we send the connection response to.
            // For this reason we handle this specific case through a middleware where we do have the
            // connection from which the trust ping message came
            // TODO: should we also move the other events to here, or should we keep it as is for the rest?
            if (messageContext.GetMessageType() == MessageTypes.TrustPingMessageType)
            {
                var message = messageContext.GetMessage<TrustPingMessage>();

                var THConnection = _cache.Get<TestHarnessConnection>(messageContext.Connection.Id);

                if (THConnection != null && THConnection.State == TestHarnessConnectionState.Responded)
                {
                    THConnection.State = TestHarnessConnectionState.Complete;
                }
            }
        }
    }
}