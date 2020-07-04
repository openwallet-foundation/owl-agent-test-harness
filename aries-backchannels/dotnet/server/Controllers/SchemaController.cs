using System;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using DotNet.Backchannel.Models;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command/schema")]
    [ApiController]
    public class SchemaController : ControllerBase
    {
        [HttpGet("{id}")]
        public async Task<IActionResult> GetSchemaByIdAsync([FromRoute] string schemaId)
        {
            throw new NotImplementedException();
        }

        [HttpPost]
        public async Task<IActionResult> SchemaOperationAsync(OperationBody body)
        {
            // Schema only has one operation
            return await this.CreateSchemaAsync(body.Data);
        }

        private async Task<IActionResult> CreateSchemaAsync(dynamic schema)
        {
            throw new NotImplementedException();
        }
    }
}
