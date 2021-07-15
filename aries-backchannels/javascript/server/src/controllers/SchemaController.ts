import { Controller, Get, PathParams, Post, BodyParams } from "@tsed/common";
import { InternalServerError, NotFound } from "@tsed/exceptions";
import { Agent } from "aries-framework";

@Controller("/agent/command/schema")
export class SchemaController {
  private agent: Agent;

  public constructor(agent: Agent) {
    this.agent = agent;
  }

  @Get("/:schemaId")
  async getSchemaById(@PathParams("schemaId") schemaId: string) {
    try {
      const schema = await this.agent.ledger.getSchema(schemaId);

      return schema;
    } catch (error) {
      // Schema does not exist on ledger
      if (error.message === "LedgerNotFound") {
        throw new NotFound(`schema with schemaId "${schemaId}" not found.`);
      }

      // All other errors
      throw new InternalServerError(
        `Error while retrieving schema with id ${schemaId}`,
        error
      );
    }
  }

  @Post()
  async createSchema(@BodyParams("data") data: any) {
    const schema = await this.agent.ledger.registerSchema({
      attributes: data.attributes,
      name: data.schema_name,
      version: data.schema_version,
    });

    return {
      schema_id: schema.id,
      schema,
    };
  }
}
