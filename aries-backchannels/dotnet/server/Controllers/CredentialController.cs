using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using Hyperledger.Aries.Features.IssueCredential;
using Hyperledger.Aries.Agents;
using Hyperledger.Aries.Utils;
using Hyperledger.Aries.Storage;
using System.Linq;
using Hyperledger.Indy.AnonCredsApi;
using Newtonsoft.Json;

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
                var credentialRecords = await _credentialService.ListAsync(context, SearchQuery.Equal(nameof(CredentialRecord.CredentialId), credentialId), 1);
                var credentialRecord = credentialRecords.First();

                var credential = await AnonCreds.ProverGetCredentialAsync(context.Wallet, credentialId);

                return Ok(new
                {
                    referent = credentialRecord.CredentialId,
                    schema_id = credentialRecord.SchemaId,
                    cred_def_id = credentialRecord.CredentialDefinitionId,
                    credential = JsonConvert.DeserializeObject(credential)
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
