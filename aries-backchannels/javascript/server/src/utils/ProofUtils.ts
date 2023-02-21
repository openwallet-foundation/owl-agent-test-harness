import { Agent, ProofRepository } from '@aries-framework/core'

export class ProofUtils {
  public static async getProofByThreadId(agent: Agent, threadId: string) {
    const proofRepository = agent.dependencyManager.resolve(ProofRepository)
    return proofRepository.getSingleByQuery(agent.context, { threadId })
  }
}
