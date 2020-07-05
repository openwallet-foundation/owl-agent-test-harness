using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;

using Hyperledger.Aries.Configuration;
using Hyperledger.Aries.Agents;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command/did")]
    [ApiController]
    public class DidController : ControllerBase
    {
        private readonly IAgentProvider _agentContextProvider;
        private readonly IProvisioningService _provisionService;

        public DidController(
            IAgentProvider agentContextProvider,
            IProvisioningService provisionService)
        {
            _agentContextProvider = agentContextProvider;
            _provisionService = provisionService;
        }


        [HttpGet]
        public async Task<IActionResult> GetPublicDid()
        {
            var context = await _agentContextProvider.GetContextAsync();
            var issuer = await _provisionService.GetProvisioningAsync(context.Wallet);

            return Ok(new
            {
                did = issuer.IssuerDid,
                verkey = issuer.IssuerVerkey
            });
        }
    }
}
