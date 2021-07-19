import { Controller, Get, Res } from "@tsed/common";
import packageJson from "../../package.json";

@Controller("/agent/command")
export class AgentStatusController {
  @Get("/status")
  getStatus(@Res() response: Res) {
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

  @Get("/version")
  getVersion(@Res() response: Res) {
    return packageJson.version;
  }
}
