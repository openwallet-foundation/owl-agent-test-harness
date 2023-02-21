import { Agent, CredentialRepository } from '@aries-framework/core'
import { AnonCredsCredentialInfo, AnonCredsCredentialRepository } from '@aries-framework/anoncreds'

export class CredentialUtils {
  public static async getCredentialByThreadId(agent: Agent, threadId: string) {
    const credentialRepository = agent.dependencyManager.resolve(CredentialRepository)
    return credentialRepository.getSingleByQuery(agent.context, { threadId })
  }

  public static async getAnonCredsCredentialById(agent: Agent, credentialId: string): Promise<AnonCredsCredentialInfo> {
    const credentialRepository = agent.dependencyManager.resolve(AnonCredsCredentialRepository)
    const credentialRecord = await credentialRepository.getByCredentialId(agent.context, credentialId)
    const attributes: { [key: string]: string } = {}
    for (const attribute in credentialRecord.credential.values) {
      attributes[attribute] = credentialRecord.credential.values[attribute].raw
    }
    return {
      attributes,
      credentialDefinitionId: credentialRecord.credential.cred_def_id,
      credentialId: credentialRecord.credentialId,
      schemaId: credentialRecord.credential.schema_id,
      credentialRevocationId: credentialRecord.credentialRevocationId,
      revocationRegistryId: credentialRecord.credential.rev_reg_id,
    }
  }
}
