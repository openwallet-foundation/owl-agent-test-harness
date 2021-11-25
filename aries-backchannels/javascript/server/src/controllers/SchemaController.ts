import { Controller, Get, PathParams, Post, BodyParams } from '@tsed/common'
import { InternalServerError, NotFound } from '@tsed/exceptions'
import { Agent } from '@aries-framework/core'
import { Schema } from 'indy-sdk'

@Controller('/agent/command/schema')
export class SchemaController {
  private agent: Agent
  private createdSchemas: {
    [schemaName: string]: Schema
  } = {}

  public constructor(agent: Agent) {
    this.agent = agent
  }

  @Get('/:schemaId')
  async getSchemaById(@PathParams('schemaId') schemaId: string): Promise<Schema> {
    try {
      const schema = await this.agent.ledger.getSchema(schemaId)

      return schema
    } catch (error) {
      // Schema does not exist on ledger
      if (error.message === 'LedgerNotFound') {
        throw new NotFound(`schema with schemaId "${schemaId}" not found.`)
      }

      // All other errors
      throw new InternalServerError(`Error while retrieving schema with id ${schemaId}`, error)
    }
  }

  @Post()
  async createSchema(@BodyParams('data') data: any) {
    if (this.createdSchemas[data.schema_name]) {
      const schema = this.createdSchemas[data.schema_name]

      return {
        schema_id: schema.id,
        schema,
      }
    }

    const schema = await this.agent.ledger.registerSchema({
      attributes: data.attributes,
      name: data.schema_name,
      version: data.schema_version,
    })

    this.createdSchemas[schema.name] = schema

    return {
      schema_id: schema.id,
      schema,
    }
  }
}
