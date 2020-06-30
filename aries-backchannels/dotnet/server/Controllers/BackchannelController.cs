using System;
using Microsoft.AspNetCore.Mvc;

namespace DotNet.Backchannel.Controllers
{
    [Route("backchannel/command")]
    [ApiController]
    public class BackchannelController : ControllerBase
    {
        [HttpPost("start-agent")]
        public void StartAgent()
        {
            throw new NotImplementedException();
        }

        [HttpPost("stop-agent")]
        public void StopAgent()
        {
            throw new NotImplementedException();
        }

        [HttpGet("agent-status")]
        public void AgentStatus()
        {
            throw new NotImplementedException();
        }
    }
}
