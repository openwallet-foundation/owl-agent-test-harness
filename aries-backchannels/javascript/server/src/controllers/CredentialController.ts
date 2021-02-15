import { Controller, Get, PathParams } from "@tsed/common";
import { Agent } from "aries-framework-javascript";

@Controller("/agent/command/credential")
export class CredentialController {
  private agent: Agent;

  public constructor(agent: Agent) {
    this.agent = agent;
  }

  @Get("/:credentialId")
  async getCredentialById(@PathParams("credentialId") credentialId: string) {
    const indyCredential = await this.agent.credentials.getIndyCredential(
      credentialId
    );

    // TODO: add state 'done' check
    return {
      referent: indyCredential.referent,
      schema_id: indyCredential.schemaId,
      cred_def_id: indyCredential.credentialDefinitionId,
      credential: indyCredential.toJSON(),
    };
  }
}
