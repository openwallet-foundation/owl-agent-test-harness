import { AnonCredsSchema } from '@aries-framework/anoncreds'
import { Controller, Get, PathParams, Post, BodyParams } from '@tsed/common'
import { InternalServerError, NotFound } from '@tsed/exceptions'
import { BaseController } from '../BaseController'
import { TestHarnessConfig } from '../TestHarnessConfig'

@Controller('/agent/command/schema')
export class SchemaController extends BaseController {
  private createdSchemas: {
    [schemaName: string]: AnonCredsSchema
  } = {}

  public constructor(testHarnessConfig: TestHarnessConfig) {
    super(testHarnessConfig)
  }

  @Get('/:schemaId')
  async getSchemaById(@PathParams('schemaId') schemaId: string): Promise<AnonCredsSchema> {
    try {
      const { schema } = await this.agent.modules.anoncreds.getSchema(schemaId)

      if (!schema) {
        throw new NotFound(`schema with schemaId "${schemaId}" not found.`)
      }
      return schema
    } catch (error: any) {
      // Schema does not exist on ledger
      if (error instanceof NotFound) {
        throw error
      }

      // All other errors
      throw new InternalServerError(`Error while retrieving schema with id ${schemaId}`, error)
    }
  }

  @Post()
  async createSchema(@BodyParams('data') data: any) {

    // TODO: use SchemaRepository
    if (this.createdSchemas[data.schema_name]) {
      const schema = this.createdSchemas[data.schema_name]

      return {
        schema_id: schema.name, // FIXME
        schema,
      }
    }

    const schema = await this.agent.modules.anoncreds.registerSchema({
      schema: {
        attrNames: data.attributes,
        name: data.schema_name,
        version: data.schema_version,
        issuerId: this.agent.context.wallet.publicDid!.did,
      },
      options: {}
    })

    if (!schema.schemaState.schema) {
      throw new Error('Schema could not be registered') // TODO
    }
    this.createdSchemas[data.schema_name] = schema.schemaState.schema

    return {
      schema_id: schema.schemaState.schemaId,
      schema: schema.schemaState.schema,
    }
  }
}
