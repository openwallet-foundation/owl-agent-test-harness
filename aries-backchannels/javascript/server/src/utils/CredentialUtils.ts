import { Agent, CredentialRepository } from "aries-framework";
import { IndyHolderService } from "aries-framework/build/src/modules/indy/services/IndyHolderService";

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

  public async getIndyCredentialById(credentialId: string) {
    const holderService =
      this.agent.injectionContainer.resolve(IndyHolderService);
    const indyCredential = await holderService.getCredential(credentialId);

    return indyCredential;
  }
}
