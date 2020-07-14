
using System;
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
            AddCredentialHandler();
            AddProofHandler();
            AddForwardHandler();
        }
    }
}