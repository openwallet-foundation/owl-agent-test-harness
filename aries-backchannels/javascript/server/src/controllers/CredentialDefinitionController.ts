import { Controller, Get, PathParams, Post, BodyParams } from "@tsed/common";
import { InternalServerError, NotFound } from "@tsed/exceptions";
import { Agent, IndyAgentService } from "@aries-framework/core";
import type * as Indy from "indy-sdk";

@Controller("/agent/command/credential-definition")
export class CredentialDefinitionController {
  private agent: Agent;

  public constructor(agent: Agent) {
    this.agent = agent;
  }

  @Get("/:credentialDefinitionId")
  async getCredentialDefinitionById(
    @PathParams("credentialDefinitionId") credentialDefinitionId: string
  ): Promise<Indy.CredDef> {
    try {
      const credentialDefinition =
        await this.agent.ledger.getCredentialDefinition(credentialDefinitionId);

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
        `Error while retrieving credential definition with id ${credentialDefinitionId}`,
        error
      );
    }
  }

  @Post()
  async createCredentialDefinition(
    @BodyParams("data")
    data: {
      tag: string;
      support_revocation: boolean;
      schema_id: string;
    }
  ): Promise<{
    credential_definition_id: string;
    credential_definition: Indy.CredDef;
  }> {
    // TODO: handle schema not found exception
    try {
      const schema = await this.agent.ledger.getSchema(data.schema_id);

      const credentialDefinition =
        await this.agent.ledger.registerCredentialDefinition({
          schema,
          supportRevocation: data.support_revocation,
          tag: data.tag,
        });

      return {
        credential_definition_id: credentialDefinition.id,
        credential_definition: credentialDefinition,
      };
    } catch (error) {
      throw new InternalServerError(
        `Error registering credential definition: ${error.message}`,
        error
      );
    }
  }
}
