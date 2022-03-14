import { Agent, CredentialRepository } from '@aries-framework/core'
import type * as Indy from 'indy-sdk'
import { IndyHolderService } from '@aries-framework/core/build/modules/indy/services/IndyHolderService'

export class CredentialUtils {
  public static async getCredentialByThreadId(agent: Agent, threadId: string) {
    const credentialRepository = agent.injectionContainer.resolve(CredentialRepository)
    return credentialRepository.getSingleByQuery({ threadId })
  }

  public static async getIndyCredentialById(agent: Agent, credentialId: string): Promise<Indy.IndyCredentialInfo> {
    const holderService = agent.injectionContainer.resolve(IndyHolderService)
    const indyCredential = await holderService.getCredential(credentialId)

    return indyCredential
  }
}
