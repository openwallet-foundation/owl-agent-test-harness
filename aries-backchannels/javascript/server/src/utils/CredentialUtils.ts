import { Agent, CredentialRepository } from '@aries-framework/core'
import type * as Indy from 'indy-sdk'
import { IndyHolderService } from '@aries-framework/core/build/modules/indy/services/IndyHolderService'

export class CredentialUtils {
  private agent: Agent
  private credentialRepository: CredentialRepository
  private holderService: IndyHolderService

  constructor(agent: Agent) {
    this.agent = agent
    this.credentialRepository = this.agent.injectionContainer.resolve(CredentialRepository)
    this.holderService = this.agent.injectionContainer.resolve(IndyHolderService)
  }

  public async getCredentialByThreadId(threadId: string) {
    return this.credentialRepository.getSingleByQuery({ threadId })
  }

  public async getIndyCredentialById(credentialId: string): Promise<Indy.IndyCredentialInfo> {
    const indyCredential = await this.holderService.getCredential(credentialId)

    return indyCredential
  }
}
