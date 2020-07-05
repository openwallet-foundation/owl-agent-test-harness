using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using DotNet.Backchannel.Models;

using Hyperledger.Aries.Features.IssueCredential;
using Hyperledger.Aries.Agents;
using Hyperledger.Aries.Configuration;
using System.Net.Mime;
using Hyperledger.Indy;
using System.Text.Json;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command/credential-definition")]
    [ApiController]
    public class CredentialDefinitionController : ControllerBase
    {
        private readonly IAgentProvider _agentContextProvider;
        private readonly IProvisioningService _provisionService;
        private readonly ISchemaService _schemaService;

        public CredentialDefinitionController(
            IAgentProvider agentContextProvider,
            IProvisioningService provisionService,
            ISchemaService schemaService)
        {
            _agentContextProvider = agentContextProvider;
            _provisionService = provisionService;
            _schemaService = schemaService;
        }

        [HttpGet("{credentialDefinitionId}")]
        public async Task<IActionResult> GetCredentialDefinitionByIdAsync([FromRoute] string credentialDefinitionId)
        {
            var context = await _agentContextProvider.GetContextAsync();

            try
            {
                var credentialDefinition = await _schemaService.LookupCredentialDefinitionAsync(context, credentialDefinitionId);
                return Content(credentialDefinition, MediaTypeNames.Application.Json);
            }
            catch (IndyException indyException)
            {
                if (indyException.SdkErrorCode == 309) return NotFound();
                else return StatusCode(500);
            }
        }

        [HttpPost]
        public async Task<IActionResult> CredentialDefinitionOperationAsync(OperationBody body)
        {
            // Credential Defintion only has one operation
            return await this.CreateCredentialDefinitionAsync(body.Data);
        }

        private async Task<IActionResult> CreateCredentialDefinitionAsync(JsonElement credentialDefinition)
        {
            var context = await _agentContextProvider.GetContextAsync();
            var issuer = await _provisionService.GetProvisioningAsync(context.Wallet);

            var credentialDefinitionId = await _schemaService.CreateCredentialDefinitionAsync(context, new CredentialDefinitionConfiguration
            {
                SchemaId = credentialDefinition.GetProperty("schema_id").GetString(),
                Tag = credentialDefinition.GetProperty("tag").GetString(),
                EnableRevocation = credentialDefinition.GetProperty("support_revocation").GetBoolean(),
                IssuerDid = issuer.IssuerDid
            });

            return Ok(new
            {
                credential_definition_id = credentialDefinitionId
            });
        }
    }
}
