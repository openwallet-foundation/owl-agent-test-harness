import { Controller, Get, Res } from "@tsed/common";

@Controller("/agent/command/status")
export class AgentStatusController {
  @Get()
  get(@Res() response: Res) {
    // NOTE: Because the agent runs inside the backchannel (not separate processes)
    // The agent is active as long as the backchannel is active
    const active = true;

    if (!active) {
      response.status(418);
      return {
        status: "inactive",
      };
    }

    return {
      status: "active",
    };
  }
}
