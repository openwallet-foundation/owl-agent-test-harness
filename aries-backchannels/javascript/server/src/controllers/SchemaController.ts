import { AnonCredsSchema, AnonCredsSchemaRepository } from '@aries-framework/anoncreds'
import { DidInfo } from '@aries-framework/core'
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
  async createSchema(@BodyParams('data') data: any): Promise<{schema_id: string, schema: AnonCredsSchema}> {

    const schemaRepository = this.agent.dependencyManager.resolve(AnonCredsSchemaRepository)

    const [schemaRecord] = await schemaRepository.findByQuery(this.agent.context, { schemaName: data.name })
    if (schemaRecord) {

      return {
        schema_id: schemaRecord.schemaId,
        schema: schemaRecord.schema,
      }
    }
  
    const publicDidInfoRecord = await this.agent.genericRecords.findById('PUBLIC_DID_INFO')
    
    if (!publicDidInfoRecord) {
      throw new Error('Agent does not have any public did')
    }

    const issuerId = (publicDidInfoRecord.content.didInfo as unknown as DidInfo).did
    const schema = await this.agent.modules.anoncreds.registerSchema({
      schema: {
        attrNames: data.attributes,
        name: data.schema_name,
        version: data.schema_version,
        issuerId,
      },
      options: { didIndyNamespace: 'main-pool'}
    })

    if (!schema.schemaState.schema || !schema.schemaState.schemaId) {
      throw new Error(`Schema could not be registered: ${JSON.stringify(schema.schemaState)}}`) // TODO
    }

    return {
      schema_id: schema.schemaState.schemaId,
      schema: schema.schemaState.schema,
    }
  }
}
