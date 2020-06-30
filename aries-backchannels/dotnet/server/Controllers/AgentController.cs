using Microsoft.AspNetCore.Mvc;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command")]
    [ApiController]
    public class AgentController : ControllerBase
    {
        [HttpGet("status")]
        public IActionResult AgentStatus()
        {
            // TODO: return status 418 if not active
            return StatusCode(200);
        }
    }
}
