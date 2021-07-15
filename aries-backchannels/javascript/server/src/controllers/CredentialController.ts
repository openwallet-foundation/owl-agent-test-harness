import { Controller, Get, PathParams } from "@tsed/common";
import { Agent } from "aries-framework";
import { IndyHolderService } from "aries-framework/build/src/modules/indy";

@Controller("/agent/command/credential")
export class CredentialController {
  private agent: Agent;

  public constructor(agent: Agent) {
    this.agent = agent;
  }

  @Get("/:credentialId")
  async getCredentialById(@PathParams("credentialId") credentialId: string) {
    const holderService = this.agent.injectionContainer.resolve(IndyHolderService)
    const indyCredential = await holderService.getCredential(credentialId)


    return indyCredential
  }
}
