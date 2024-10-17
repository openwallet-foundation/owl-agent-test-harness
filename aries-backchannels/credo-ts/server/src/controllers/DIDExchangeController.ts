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
  ReceiveOutOfBandImplicitInvitationConfig,
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

  @Post('/create-request-resolvable-did')
  async createRequestResolvableDID(@BodyParams() data: { data: { their_public_did: string } }) {
    const { their_public_did } = data.data;

    const { outOfBandRecord, connectionRecord } = await this.agent.oob.receiveImplicitInvitation({ did: their_public_did } as ReceiveOutOfBandImplicitInvitationConfig);
    //const request = await this.agent.connections.createRequest(their_public_did);

    // their_public_did = data["their_public_did"]
    // agent_operation = (
    //     f"{agent_operation}create-request?their_public_did={their_public_did}"
    // )
    // data = None

    // Add the two records to the response and move the state from the connectionRecord to the root of connectionRecords.
    const connectionRecords = {
      ...(connectionRecord && { connectionRecord }),
      ...(outOfBandRecord && { outOfBandRecord }),
      ...(connectionRecord && { state: connectionRecord.state }),
      ...(connectionRecord && { connection_id: connectionRecord.outOfBandId })
    }

    return connectionRecords
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