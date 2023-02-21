import { Controller, Get, PathParams, Post, BodyParams } from '@tsed/common'
import { InternalServerError, NotFound } from '@tsed/exceptions'
import { BaseController } from '../BaseController'
import { TestHarnessConfig } from '../TestHarnessConfig'
import { AnonCredsApi, AnonCredsCredentialDefinition } from '@aries-framework/anoncreds'
import { DidInfo } from '@aries-framework/core'

@Controller('/agent/command/credential-definition')
export class CredentialDefinitionController extends BaseController {
  public constructor(testHarnessConfig: TestHarnessConfig) {
    super(testHarnessConfig)
  }

  @Get('/:credentialDefinitionId')
  async getCredentialDefinitionById(
    @PathParams('credentialDefinitionId') credentialDefinitionId: string
  ): Promise<AnonCredsCredentialDefinition> {
    try {
      const { credentialDefinition } = await this.agent.modules.anoncreds.getCredentialDefinition(credentialDefinitionId)

      if (!credentialDefinition) {
        throw new NotFound(`credential definition with credentialDefinitionId "${credentialDefinitionId}" not found.`)
      }
      return credentialDefinition
    } catch (error) {
      // Credential definition does not exist on ledger
      if (error instanceof NotFound) {
        throw error
      }

      // All other errors
      throw new InternalServerError(
        `Error while retrieving credential definition with id ${credentialDefinitionId}`,
        error
      )
    }
  }

  @Post()
  async createCredentialDefinition(
    @BodyParams('data')
    data: {
      tag: string
      support_revocation: boolean
      schema_id: string
    }
  ): Promise<{
    credential_definition_id: string
    credential_definition: AnonCredsCredentialDefinition
  }> {
    // TODO: handle schema not found exception
    try {

      const anoncredsApi = this.agent.dependencyManager.resolve(AnonCredsApi)

      const schema = await anoncredsApi.getSchema(data.schema_id)

      const publicDidInfoRecord = await this.agent.genericRecords.findById('PUBLIC_DID_INFO')
    
      if (!publicDidInfoRecord) {
        throw new Error('Agent does not have any public did')
      }
  
      const issuerId = (publicDidInfoRecord.content.didInfo as unknown as DidInfo).did
      
      const { credentialDefinitionState } = await anoncredsApi.registerCredentialDefinition({ 
        credentialDefinition: {
          issuerId,
          schemaId: schema.schemaId,
          tag: data.tag,
        }, options: { didIndyNamespace: 'main-pool'}}) 

      if (!credentialDefinitionState.credentialDefinition || !credentialDefinitionState.credentialDefinitionId) {
        throw new Error()
      }
      
      return {
        credential_definition_id: credentialDefinitionState.credentialDefinitionId,
        credential_definition: credentialDefinitionState.credentialDefinition,
      }
    } catch (error: any) {
      throw new InternalServerError(`Error registering credential definition: ${error.message}`, error)
    }
  }
}
