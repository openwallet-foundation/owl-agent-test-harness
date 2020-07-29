using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using Hyperledger.Aries.Features.IssueCredential;
using Hyperledger.Aries.Agents;
using Hyperledger.Aries.Utils;

namespace DotNet.Backchannel.Controllers
{

    [Route("agent/command/credential")]
    [ApiController]
    public class CredentialController : ControllerBase
    {
        private readonly ICredentialService _credentialService;
        private readonly IAgentProvider _agentContextProvider;

        public CredentialController(
            ICredentialService credentialService,
            IAgentProvider agentContextProvider
        )
        {
            _credentialService = credentialService;
            _agentContextProvider = agentContextProvider;
        }

        [HttpGet("{credentialId}")]
        public async Task<IActionResult> GetCredentialById([FromRoute] string credentialId)
        {
            var context = await _agentContextProvider.GetContextAsync();

            try
            {
                var credentialRecord = await _credentialService.GetAsync(context, credentialId);

                if (credentialRecord.GetTag(TagConstants.Role) != TagConstants.Holder)
                {
                    // We should only return the credential if we are the holder
                    return NotFound();
                }

                // TODO: should we return extra data?
                return Ok(new
                {
                    referent = credentialRecord.Id,
                    schema_id = credentialRecord.SchemaId,
                    cred_def_id = credentialRecord.CredentialDefinitionId
                });
            }
            catch
            {
                // Unable to retrieve credential record.
                return NotFound();
            }
        }
    }
}
