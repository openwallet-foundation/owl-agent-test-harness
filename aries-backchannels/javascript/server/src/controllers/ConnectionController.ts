import { Controller, Get, PathParams, Post, BodyParams } from '@tsed/common'
import { NotFound } from '@tsed/exceptions'
import {
  ConnectionRecord,
  ConnectionInvitationMessage,
  JsonTransformer,
  AgentConfig,
  ConnectionEventTypes,
  ConnectionStateChangedEvent,
  ConnectionState,
} from '@aries-framework/core'

import { replaceNewDidCommPrefixWithLegacyDidSovOnMessage } from '@aries-framework/core/build/utils/messageType'
import { ReplaySubject } from 'rxjs'
import { BaseController } from '../BaseController'
import { TestHarnessConfig } from '../TestHarnessConfig'

@Controller('/agent/command/connection')
export class ConnectionController extends BaseController {
  private subject = new ReplaySubject<ConnectionStateChangedEvent>()

  public constructor(testHarnessConfig: TestHarnessConfig) {
    super(testHarnessConfig)
  }

  onStartup = () => {
    this.subject = new ReplaySubject<ConnectionStateChangedEvent>()
    // Catch all events in replay subject for later use
    this.agent.events
      .observable<ConnectionStateChangedEvent>(ConnectionEventTypes.ConnectionStateChanged)
      .subscribe(this.subject)
  }

  @Get('/:connectionId')
  async getConnectionById(@PathParams('connectionId') connectionId: string) {
    const connection = await this.agent.connections.findById(connectionId)

    if (!connection) {
      throw new NotFound(`connection with connectionId "${connectionId}" not found.`)
    }

    return this.mapConnection(connection)
  }

  @Get('/')
  async getAllConnections() {
    const connections = await this.agent.connections.getAll()

    return connections.map((conn) => this.mapConnection(conn))
  }

  @Post('/create-invitation')
  async createInvitation(@BodyParams('data') data?: { mediator_connection_id?: string }) {
    const mediatorId = await this.mediatorIdFromMediatorConnectionId(data?.mediator_connection_id)

    const { invitation, connectionRecord } = await this.agent.connections.createConnection({
      mediatorId,
      // Needed to complete connection: https://github.com/hyperledger/aries-framework-javascript/issues/668
      autoAcceptConnection: true,
    })

    const invitationJson = invitation.toJSON()

    const config = this.agent.injectionContainer.resolve(AgentConfig)
    if (config.useLegacyDidSovPrefix) {
      replaceNewDidCommPrefixWithLegacyDidSovOnMessage(invitationJson)
    }

    return {
      ...this.mapConnection(connectionRecord),
      invitation: invitationJson,
    }
  }

  @Post('/receive-invitation')
  async receiveInvitation(@BodyParams('data') data: Record<string, unknown> & { mediator_connection_id?: string }) {
    const { mediator_connection_id, ...invitation } = data

    const mediatorId = await this.mediatorIdFromMediatorConnectionId(mediator_connection_id)

    const connection = await this.agent.connections.receiveInvitation(
      JsonTransformer.fromJSON(invitation, ConnectionInvitationMessage),
      {
        mediatorId,
        // Needed to complete connection: https://github.com/hyperledger/aries-framework-javascript/issues/668
        autoAcceptConnection: true,
      }
    )

    return this.mapConnection(connection)
  }

  @Post('/accept-invitation')
  async acceptInvitation(@BodyParams('id') connectionId: string) {
    const connection = await this.agent.connections.getById(connectionId)
    return this.mapConnection(connection)
  }

  @Post('/accept-request')
  async acceptRequest(@BodyParams('id') connectionId: string) {
    const connection = await this.agent.connections.getById(connectionId)
    return this.mapConnection(connection)
  }

  @Post('/send-ping')
  async sendPing(
    @BodyParams('id') connectionId: string,
    // For now we ignore data. This could contain a comment property,
    // AFJ doesn't support passing it for now
    @BodyParams('data') data: any
  ) {
    const connection = await this.agent.connections.getById(connectionId)
    return this.mapConnection(connection)
  }

  private async mediatorIdFromMediatorConnectionId(mediatorConnectionId?: string): Promise<string | undefined> {
    if (!mediatorConnectionId) return undefined

    // Find mediator id if mediator connection id is provided
    const mediator = await this.agent.mediationRecipient.findByConnectionId(mediatorConnectionId)

    return mediator?.id
  }

  private mapConnection(connection: ConnectionRecord) {
    return {
      // If we use auto accept, we can't include the state as we will move quicker than the calls in the test harness. This will
      // make verification fail. The test harness recognizes the 'N/A' state.
      state: connection.state === ConnectionState.Complete ? connection.state : 'N/A',
      connection_id: connection.id,
      connection,
    }
  }
}
