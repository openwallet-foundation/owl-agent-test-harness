import { Controller, Get, PathParams } from "@tsed/common";
import { Agent } from "aries-framework";

@Controller("/agent/command/credential")
export class CredentialController {
  private agent: Agent;

  public constructor(agent: Agent) {
    this.agent = agent;
  }

  @Get("/:credentialId")
  async getCredentialById(@PathParams("credentialId") credentialId: string) {
    return await this.agent.credentials.getById(credentialId);
  }
}
