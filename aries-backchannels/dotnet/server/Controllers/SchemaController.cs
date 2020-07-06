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

        private async Task<IActionResult> CreateSchemaAsync(JsonElement schema)
        {
            var context = await _agentContextProvider.GetContextAsync();
            var issuer = await _provisionService.GetProvisioningAsync(context.Wallet);

            var schemaName = schema.GetProperty("schema_name").GetString();
            var schemaVersion = schema.GetProperty("schema_version").GetString();

            // TODO: There should be a cleaner approach
            var schemaAttributes = new List<string>();
            foreach (JsonElement attribute in schema.GetProperty("attributes").EnumerateArray())
            {
                schemaAttributes.Add(attribute.GetString());
            }

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
                    attributeNames: schemaAttributes.ToArray()
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
