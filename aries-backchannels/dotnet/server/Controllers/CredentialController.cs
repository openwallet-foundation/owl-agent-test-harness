using System;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command/credential")]
    [ApiController]
    public class CredentialController : ControllerBase
    {
        [HttpGet("{id}")]
        public async Task<IActionResult> GetCredentialById([FromRoute] string credentialId)
        {
            throw new NotImplementedException();
        }
    }
}
