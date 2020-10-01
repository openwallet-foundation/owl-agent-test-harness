import { Controller, Get, PathParams, Post, BodyParams } from "@tsed/common";
import { InternalServerError, NotFound } from "@tsed/exceptions";
import { Agent } from "aries-framework-javascript";

@Controller("/agent/command/credential-definition")
export class CredentialDefinitionController {
  private agent: Agent;

  public constructor(agent: Agent) {
    this.agent = agent;
  }

  @Get("/:credentialDefinitionId")
  async getCredentialDefinitionById(
    @PathParams("credentialDefinitionId") credentialDefinitionId: string
  ) {
    try {
      const [
        ,
        credentialDefinition,
      ] = await this.agent.ledger.getCredentialDefinition(
        credentialDefinitionId
      );

      return credentialDefinition;
    } catch (error) {
      // Credential definition does not exist on ledger
      if (error.message === "LedgerNotFound") {
        throw new NotFound(
          `credential definition with credentialDefinitionId "${credentialDefinitionId}" not found.`
        );
      }

      // All other errors
      throw new InternalServerError(
        `Error while retrieving credential definition  with id ${credentialDefinitionId}`,
        error
      );
    }
  }

  @Post()
  async createCredentialDefinition(@BodyParams("data") data: any) {
    // TODO: handle schema not found exception
    const [, schema] = await this.agent.ledger.getSchema(data.schema_id);

    const [
      credentialDefinition,
      credentialDefinitionId,
    ] = await this.agent.ledger.registerCredentialDefinition({
      tag: data.tag,
      config: {
        support_revocation: data.support_revocation,
      },
      schema,
      signatureType: "CL",
    });

    return {
      credential_definition_id: credentialDefinitionId,
      credential_definition: credentialDefinition,
    };
  }
}
