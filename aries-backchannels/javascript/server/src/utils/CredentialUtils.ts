import { Agent, CredentialRepository } from "aries-framework";

export class CredentialUtils {
  private agent: Agent;
  private credentialRepository: CredentialRepository;

  constructor(agent: Agent) {
    this.agent = agent;
    this.credentialRepository =
      this.agent.injectionContainer.resolve(CredentialRepository);
  }

  public async getCredentialByThreadId(threadId: string) {
    try {
      return await this.credentialRepository.getSingleByQuery({ threadId });
    } catch (e) {
      return false;
    }
  }
}
