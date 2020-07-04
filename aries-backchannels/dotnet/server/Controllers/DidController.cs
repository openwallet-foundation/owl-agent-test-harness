using System;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command/did")]
    [ApiController]
    public class DidController : ControllerBase
    {
        [HttpGet]
        public async Task<IActionResult> GetPublicDid()
        {
            throw new NotImplementedException();
        }
    }
}
