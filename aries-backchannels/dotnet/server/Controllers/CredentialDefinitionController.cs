using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using DotNet.Backchannel.Models;

using Hyperledger.Aries.Features.IssueCredential;
using Hyperledger.Aries.Agents;
using Hyperledger.Aries.Configuration;
using System.Net.Mime;
using Hyperledger.Indy;
using System.Text.Json;
using Newtonsoft.Json.Linq;

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
            var credentialDefintion = await this.LookupCredentialDefinitionByIdAsync(credentialDefinitionId);

            if (credentialDefintion != null)
            {
                return Content(credentialDefintion, MediaTypeNames.Application.Json);
            }

            return NotFound();
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

            var schemaId = credentialDefinition.GetProperty("schema_id").GetString();
            var tag = credentialDefinition.GetProperty("tag").GetString();
            var supportRevocation = credentialDefinition.GetProperty("support_revocation").GetBoolean();

            // Needed to construct credential definition id
            var schema = JObject.Parse(await _schemaService.LookupSchemaAsync(context, schemaId));
            var schemaSeqNo = schema["seqNo"].ToString();
            var signatureType = "CL"; // TODO: can we make this variable?

            // The test client sends multiple create credential definition requests with
            // the same parameters. First check whether the credential definition already exists.
            var credentialDefinitionId = $"{issuer.IssuerDid}:3:{signatureType}:{schemaSeqNo}:{tag}";
            var credentialDefinitionString = await this.LookupCredentialDefinitionByIdAsync(credentialDefinitionId);

            // If the credential defintion doesn't already exists, create it
            if (credentialDefinitionString == null)
            {
                await _schemaService.CreateCredentialDefinitionAsync(context, new CredentialDefinitionConfiguration
                {
                    SchemaId = schemaId,
                    Tag = tag,
                    EnableRevocation = supportRevocation,
                    IssuerDid = issuer.IssuerDid
                });
            }

            return Ok(new
            {
                credential_definition_id = credentialDefinitionId
            });
        }

        private async Task<string> LookupCredentialDefinitionByIdAsync(string credentialDefinitionId)
        {
            var context = await _agentContextProvider.GetContextAsync();

            try
            {
                var credentialDefintion = await _schemaService.LookupCredentialDefinitionAsync(context, credentialDefinitionId);
                return credentialDefintion;
            }
            catch (IndyException)
            {
                return null;
            }
        }
    }
}
