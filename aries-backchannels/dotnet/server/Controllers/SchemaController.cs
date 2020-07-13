using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using DotNet.Backchannel.Models;
using System.Net.Mime;

using Hyperledger.Aries.Agents;
using Hyperledger.Aries.Configuration;
using Hyperledger.Aries.Features.IssueCredential;
using Hyperledger.Indy;
using Newtonsoft.Json.Linq;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command/schema")]
    [ApiController]
    public class SchemaController : ControllerBase
    {
        private readonly IAgentProvider _agentContextProvider;
        private readonly IProvisioningService _provisionService;
        private readonly ISchemaService _schemaService;

        public SchemaController(
            IAgentProvider agentContextProvider,
            IProvisioningService provisionService,
            ISchemaService schemaService)
        {
            _agentContextProvider = agentContextProvider;
            _provisionService = provisionService;
            _schemaService = schemaService;
        }

        [HttpGet("{schemaId}")]
        public async Task<IActionResult> GetSchemaByIdAsync([FromRoute] string schemaId)
        {
            var schema = await this.LookupSchemaByIdAsync(schemaId);

            if (schema != null)
            {
                return Content(schema, MediaTypeNames.Application.Json);
            }

            return NotFound();
        }

        [HttpPost]
        public async Task<IActionResult> SchemaOperationAsync(OperationBody body)
        {
            // Schema only has one operation
            return await this.CreateSchemaAsync(body.Data);
        }

        private async Task<IActionResult> CreateSchemaAsync(JObject schema)
        {
            var context = await _agentContextProvider.GetContextAsync();
            var issuer = await _provisionService.GetProvisioningAsync(context.Wallet);

            var schemaName = (string)schema["schema_name"];
            var schemaVersion = (string)schema["schema_version"];
            var schemaAttributes = schema["attributes"].ToObject<string[]>();

            // The test client sends multiple create schema requests with
            // the same parameters. First check whether the schema already exists.
            var schemaId = $"{issuer.IssuerDid}:2:{schemaName}:{schemaVersion}";
            var schemaString = await this.LookupSchemaByIdAsync(schemaId);

            // If the schema doesn't already exists, create it
            if (schemaString == null)
            {
                await _schemaService.CreateSchemaAsync(
                    context: context,
                    issuerDid: issuer.IssuerDid,
                    name: schemaName,
                    version: schemaVersion,
                    attributeNames: schemaAttributes
                );
            }

            return Ok(new
            {
                schema_id = schemaId
            });
        }

        private async Task<string> LookupSchemaByIdAsync(string schemaId)
        {
            var context = await _agentContextProvider.GetContextAsync();

            try
            {
                var schema = await _schemaService.LookupSchemaAsync(context, schemaId);
                return schema;
            }
            catch (IndyException)
            {
                return null;
            }
        }
    }
}
