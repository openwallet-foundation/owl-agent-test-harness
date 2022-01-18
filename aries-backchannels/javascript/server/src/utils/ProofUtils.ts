import { Agent, ProofRepository } from '@aries-framework/core'

export class ProofUtils {
  private agent: Agent
  private proofRepository: ProofRepository

  constructor(agent: Agent) {
    this.agent = agent
    this.proofRepository = this.agent.injectionContainer.resolve(ProofRepository)
  }

  public async getProofByThreadId(threadId: string) {
    return this.proofRepository.getSingleByQuery({ threadId })
  }
}
