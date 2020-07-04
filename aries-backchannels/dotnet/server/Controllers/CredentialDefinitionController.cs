using System;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using DotNet.Backchannel.Models;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command/credential-definition")]
    [ApiController]
    public class CredentialDefinitionController : ControllerBase
    {
        [HttpGet("{id}")]
        public async Task<IActionResult> GetCredentialDefinitionByIdAsync([FromRoute] string credentialDefinitionId)
        {
            throw new NotImplementedException();
        }

        [HttpPost]
        public async Task<IActionResult> CredentialDefinitionOperationAsync(OperationBody body)
        {
            // Credential Defintion only has one operation
            return await this.CreateCredentialDefinitionAsync(body.Data);
        }

        private async Task<IActionResult> CreateCredentialDefinitionAsync(dynamic credentialDefinition)
        {
            throw new NotImplementedException();
        }
    }
}
