import { Agent, ProofRepository } from "aries-framework";

export class ProofUtils {
  private agent: Agent;
  private proofRepository: ProofRepository;

  constructor(agent: Agent) {
    this.agent = agent;
    this.proofRepository =
      this.agent.injectionContainer.resolve(ProofRepository);
  }

  public async getProofByThreadId(threadId: string) {
    try {
      return await this.proofRepository.getSingleByQuery({ threadId });
    } catch (e) {
      return false;
    }
  }
}
