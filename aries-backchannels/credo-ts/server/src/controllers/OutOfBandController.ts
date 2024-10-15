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

import { convertToNewInvitation } from '@credo-ts/core/build/modules/oob/helpers'
import { convertToOldInvitation } from '@credo-ts/core/build/modules/oob/helpers'
import { filter, firstValueFrom, ReplaySubject, tap, timeout } from 'rxjs'
import { BaseController } from '../BaseController'
import { TestHarnessConfig } from '../TestHarnessConfig'
import { ConnectionUtils } from '../utils/ConnectionUtils'

@Controller('/agent/command/out-of-band')
export class OutOfBandController extends BaseController {
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

    const routing = await this.agent.mediationRecipient.getRouting({
      mediatorId,
    })

    const outOfBandRecord = await this.agent.oob.createInvitation({
      routing,
      // Needed to complete connection: https://github.com/hyperledger/aries-framework-javascript/issues/668
      // TODO probably don't need this anymore.
      autoAcceptConnection: true,
    })

    const config = this.agent.dependencyManager.resolve(AgentConfig)
    const invitation = outOfBandRecord.outOfBandInvitation
    const invitationJson = invitation.toJSON({ useDidSovPrefixWhereAllowed: config.useDidSovPrefixWhereAllowed })

    return {
      state: OutOfBandState.Initial,
      // This should be the connection id. However, the connection id is not available until a request is received.
      // We can just use the oob invitation I guess.
      connection_id: outOfBandRecord.id,
      invitation: invitationJson,
    }
  }

  // @Post('/send-invitation-message')
  // async sendInvitationMessage(@BodyParams() invitationDetails: any) {
  //   // Implement the logic to send an invitation message
  //   // Example:
  //   const result = await this.agent.sendInvitationMessage(invitationDetails)
  //   return result
  // }

  @Post('/receive-invitation')
  async receiveInvitation(@BodyParams('data') data: Record<string, unknown> & { mediator_connection_id?: string }) {
    const { mediator_connection_id, ...invitationJson } = data as any

    const mediatorId = await this.mediatorIdFromMediatorConnectionId(mediator_connection_id)

    const routing = await this.agent.mediationRecipient.getRouting({
      mediatorId,
    })

    this.agent.config.logger.debug('invitationJson: ', invitationJson)
    const oobInvitation = JsonTransformer.fromJSON(invitationJson, OutOfBandInvitation)

    const { outOfBandRecord, connectionRecord } = await this.agent.oob.receiveInvitation(oobInvitation, {
      routing,
      autoAcceptConnection: true, //was false
      autoAcceptInvitation: true,
    })

    this.agent.config.logger.debug('OutOfBandController.receiveInvitation: outOfBandRecord: ', outOfBandRecord)
    this.agent.config.logger.debug('OutOfBandController.receiveInvitation: connectionRecord: ', connectionRecord)

    // if (!outOfBandRecord) {
    //   throw new CredoError('Processing invitation did not result in a out of band record')
    // }

    if (!connectionRecord) {
      throw new CredoError('Processing invitation did not result in a connection record')
    }

    // Credo doesn't support the send-request message. It does this at this point of accepting the invitation.
    // Therefore the state at this point in the protocol is request-sent. 
    // Set the state to invitation-received at the route of the response. This is the state that the test harness expects at this point.
    // The send-request message will just bypass any calls to Credo and set the state to request-sent.
    //connectionRecord.originalCredoState = connectionRecord.state
    if (connectionRecord.state === DidExchangeState.RequestSent) {
      connectionRecord.state = DidExchangeState.InvitationReceived
    }

    // Add the two records to the response and move the state from the connectionRecord to the root of connectionRecords.
    const connectionRecords = {
      ...(connectionRecord && { connectionRecord }),
      ...(outOfBandRecord && { outOfBandRecord }),
      ...(connectionRecord && { state: connectionRecord.state }),
      ...(connectionRecord && { connection_id: connectionRecord.outOfBandId })
    }

    //return this.mapConnection(connectionRecord)
    //return connectionRecord
    //return outOfBandRecord
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

    return this.mapConnection(connection)
  }

  @Post('/accept-invitation')
  async acceptInvitation(@BodyParams('id') id: string) {
    const connection = await ConnectionUtils.getConnectionByConnectionIdOrOutOfBandId(this.agent, id)

    return this.mapConnection(connection)
  }

  @Post('/accept-request')
  async acceptRequest(@BodyParams('id') id: string) {
    // possible here that the request hasn't finished processing yet
    //await this.waitForState(id, DidExchangeState.RequestReceived)

    const connection = await ConnectionUtils.getConnectionByConnectionIdOrOutOfBandId(this.agent, id)

    return this.mapConnection(connection)
  }

  @Post('/send-ping')
  async sendPing(
    @BodyParams('id') id: string,
    // For now we ignore data. This could contain a comment property,
    // AFJ doesn't support passing it for now
    @BodyParams('data') data: any
  ) {
    const connection = await ConnectionUtils.getConnectionByConnectionIdOrOutOfBandId(this.agent, id)

    if (!connection) throw new NotFound(`Connection with id ${id} not found`)

    return this.mapConnection(connection)
  }

  private async mediatorIdFromMediatorConnectionId(mediatorConnectionId?: string): Promise<string | undefined> {
    if (!mediatorConnectionId) return undefined

    // Find mediator id if mediator connection id is provided
    const mediator = await this.agent.mediationRecipient.findByConnectionId(mediatorConnectionId)

    return mediator?.id
  }

  // private async waitForState(id: string, state: DidExchangeState) {
  //   return await firstValueFrom(
  //     this.subject.pipe(
  //       filter((c) => c.payload.connectionRecord.id === id ),
  //       filter((c) => c.payload.connectionRecord.state === state),
  //       timeout(20000)
  //     )
  //   )
  // }

  private mapConnection(connection: ConnectionRecord) {
    return {
      // If we use auto accept, we can't include the state as we will move quicker than the calls in the test harness. This will
      // make verification fail. The test harness recognizes the 'N/A' state for some connection types.
      state: connection.state === DidExchangeState.Completed ? connection.rfc0160State : 'N/A',
      connection_id: connection.id,
      connection,
    }
  }
}