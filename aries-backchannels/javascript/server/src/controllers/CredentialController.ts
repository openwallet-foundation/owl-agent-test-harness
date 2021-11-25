import { Controller, Get, PathParams } from '@tsed/common'
import { Agent } from '@aries-framework/core'
import { CredentialUtils } from '../utils/CredentialUtils'

@Controller('/agent/command/credential')
export class CredentialController {
  private agent: Agent

  public constructor(agent: Agent) {
    this.agent = agent
  }

  @Get('/:credentialId')
  async getCredentialById(@PathParams('credentialId') credentialId: string) {
    return await new CredentialUtils(this.agent).getIndyCredentialById(credentialId)
  }
}
