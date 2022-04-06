import { Controller, Get } from '@tsed/common'
import { BaseController } from '../BaseController'
import { TestHarnessConfig } from '../TestHarnessConfig'

@Controller('/agent/command/did')
export class DidController extends BaseController {
  public constructor(testHarnessConfig: TestHarnessConfig) {
    super(testHarnessConfig)
  }

  @Get()
  getPublicDid() {
    const didInfo = this.agent.publicDid

    return didInfo
  }
}
