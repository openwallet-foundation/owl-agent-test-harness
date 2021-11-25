import { Controller, Get } from '@tsed/common'
import { Agent } from '@aries-framework/core'

@Controller('/agent/command/did')
export class DidController {
  private agent: Agent

  public constructor(agent: Agent) {
    this.agent = agent
  }

  @Get()
  getPublicDid() {
    const didInfo = this.agent.publicDid

    return didInfo
  }
}
