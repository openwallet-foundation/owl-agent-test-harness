import { Controller, Get, PathParams, Post, BodyParams } from '@tsed/common'
import { NotFound } from '@tsed/exceptions'
import {
  OutOfBandRecord,
  OutOfBandInvitation,
  ConnectionInvitationMessage,
  ConnectionRecord,
  JsonTransformer,
  AgentConfig,
  OutOfBandEventTypes,
  OutOfBandStateChangedEvent,
  OutOfBandState,
  CredoError,
  DidExchangeState,
} from '@credo-ts/core'

import { filter, firstValueFrom, ReplaySubject, tap, timeout } from 'rxjs'
import { BaseController } from '../BaseController'
import { TestHarnessConfig } from '../TestHarnessConfig'
import { ConnectionUtils } from '../utils/ConnectionUtils'

@Controller('/agent/command/did-exchange')
export class DIDExchangeController extends BaseController {
  private subject = new ReplaySubject<OutOfBandStateChangedEvent>()

  public constructor(testHarnessConfig: TestHarnessConfig) {
    super(testHarnessConfig)
  }

  onStartup = () => {
    this.subject = new ReplaySubject<OutOfBandStateChangedEvent>()
    // Catch all events in replay subject for later use
    this.agent.events
      .observable<OutOfBandStateChangedEvent>(OutOfBandEventTypes.OutOfBandStateChanged)
      .subscribe(this.subject)
  }

  @Get('/:id')
  async getConnectionById(@PathParams('id') id: string) {
    const connection = await ConnectionUtils.getConnectionByConnectionIdOrOutOfBandId(this.agent, id)

    if (!connection) throw new NotFound(`Connection with id ${id} not found`)

    return connection
  }

  // Implementing this method just to satisfy AATH. This will not call credo and just set the state that was set in the previous step of receive invitation.
  @Post('/send-request')
  async sendRequest(@BodyParams('id') id: string) {
    const connection = await ConnectionUtils.getConnectionByConnectionIdOrOutOfBandId(this.agent, id)
    
    if (!connection) {
      throw new CredoError('Connection not found')
    }

    //connection.state = DidExchangeState.RequestSent

    return connection
  }


}