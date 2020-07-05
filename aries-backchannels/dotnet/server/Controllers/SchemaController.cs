using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using System.Collections.Generic;
using DotNet.Backchannel.Models;

using Hyperledger.Aries.Agents;
using Hyperledger.Aries.Configuration;
using Hyperledger.Aries.Features.IssueCredential;
using System.Text.Json;
using System.Net.Mime;
using Hyperledger.Indy;

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
            var context = await _agentContextProvider.GetContextAsync();

            try
            {
                var schema = await _schemaService.LookupSchemaAsync(context, schemaId);
                return Content(schema, MediaTypeNames.Application.Json);
            }
            catch (IndyException indyException)
            {
                if (indyException.SdkErrorCode == 309) return NotFound();
                else return StatusCode(500);
            }
        }

        [HttpPost]
        public async Task<IActionResult> SchemaOperationAsync(OperationBody body)
        {
            // Schema only has one operation
            return await this.CreateSchemaAsync(body.Data);
        }

        private async Task<IActionResult> CreateSchemaAsync(JsonElement schema)
        {
            var context = await _agentContextProvider.GetContextAsync();
            var issuer = await _provisionService.GetProvisioningAsync(context.Wallet);

            // TODO: There should be a cleaner approach
            var attributes = new List<string>();
            foreach (JsonElement attribute in schema.GetProperty("attributes").EnumerateArray())
            {
                attributes.Add(attribute.GetString());
            }

            var schemaId = await _schemaService.CreateSchemaAsync(
                context: context,
                issuerDid: issuer.IssuerDid,
                name: schema.GetProperty("schema_name").GetString(),
                version: schema.GetProperty("schema_version").GetString(),
                attributeNames: attributes.ToArray()
            );

            return Ok(new
            {
                schema_id = schemaId
            });
        }
    }
}
