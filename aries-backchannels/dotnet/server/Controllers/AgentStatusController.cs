using Microsoft.AspNetCore.Mvc;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command/status")]
    [ApiController]
    public class AgentStatusController : ControllerBase
    {
        [HttpGet]
        public IActionResult AgentStatus()
        {
            // TODO: check whether agent is active
            var active = true;

            if (active) return Ok(new { status = "active" });
            else return StatusCode(418, new { status = "inactive" });
        }
    }
}
