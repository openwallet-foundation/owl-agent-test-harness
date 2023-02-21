import { Agent, CredentialRepository } from '@aries-framework/core'
import { AnonCredsCredentialInfo, AnonCredsCredentialRepository } from '@aries-framework/anoncreds'

export class CredentialUtils {
  public static async getCredentialByThreadId(agent: Agent, threadId: string) {
    const credentialRepository = agent.dependencyManager.resolve(CredentialRepository)
    return credentialRepository.getSingleByQuery(agent.context, { threadId })
  }

  public static async getAnonCredsCredentialById(agent: Agent, credentialId: string): Promise<Record<string, unknown>> {
    const credentialRepository = agent.dependencyManager.resolve(AnonCredsCredentialRepository)
    const credentialRecord = await credentialRepository.getByCredentialId(agent.context, credentialId)
    const attributes: { [key: string]: string } = {}
    for (const attribute in credentialRecord.credential.values) {
      attributes[attribute] = credentialRecord.credential.values[attribute].raw
    }

    return {
      attrs: attributes,
      cred_def_id: credentialRecord.credential.cred_def_id,
      referent: credentialRecord.credentialId,
      schema_id: credentialRecord.credential.schema_id,
      cred_rev_id: credentialRecord.credentialRevocationId,
      rev_reg_id: credentialRecord.credential.rev_reg_id,
    }
  }
}
