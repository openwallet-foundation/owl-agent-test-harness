
using System;
using DotNet.Backchannel.Handlers;
using Hyperledger.Aries.Agents;

namespace DotNet.Backchannel
{
    public class TestAgent : AgentBase
    {
        public TestAgent(IServiceProvider serviceProvider)
            : base(serviceProvider)
        {
        }

        protected override void ConfigureHandlers()
        {
            AddConnectionHandler();
            AddTrustPingHandler();
            AddBasicMessageHandler();
            AddProofHandler();
            AddForwardHandler();
            // We use a custom credential handler
            AddHandler<AATHCredentialHandler>();
            // Framework doesn't send ack after verifying presentation
            AddHandler<PresentationAckHandler>();
        }
    }
}