import { Controller, Get, PathParams, Post, BodyParams } from "@tsed/common";
import { NotFound } from "@tsed/exceptions";
import {
  Agent,
  ConnectionRecord,
  ConnectionInvitationMessage,
  JsonTransformer,
  AgentConfig,
  ConnectionEventTypes,
  ConnectionStateChangedEvent,
  ConnectionState,
} from "@aries-framework/core";

import { replaceNewDidCommPrefixWithLegacyDidSovOnMessage } from "@aries-framework/core/build/utils/messageType";
import { filter, firstValueFrom, ReplaySubject, timeout } from "rxjs";

@Controller("/agent/command/connection")
export class ConnectionController {
  private agent: Agent;
  private subject = new ReplaySubject<ConnectionStateChangedEvent>()

  public constructor(agent: Agent) {
    this.agent = agent;

    // Catch all events in replay subject for later use
    agent.events.observable<ConnectionStateChangedEvent>(
      ConnectionEventTypes.ConnectionStateChanged
    ).subscribe(this.subject)
  }

  @Get("/:connectionId")
  async getConnectionById(@PathParams("connectionId") connectionId: string) {
    const connection = await this.agent.connections.findById(connectionId);

    if (!connection) {
      throw new NotFound(
        `connection with connectionId "${connectionId}" not found.`
      );
    }

    return this.mapConnection(connection);
  }

  @Get("/")
  async getAllConnections() {
    const connections = await this.agent.connections.getAll();

    return connections.map((conn) => this.mapConnection(conn));
  }

  @Post("/create-invitation")
  async createInvitation() {
    const { invitation, connectionRecord } =
      await this.agent.connections.createConnection();
    const invitationJson = invitation.toJSON();

    const config = this.agent.injectionContainer.resolve(AgentConfig);
    if (config.useLegacyDidSovPrefix) {
      replaceNewDidCommPrefixWithLegacyDidSovOnMessage(invitationJson);
    }

    return {
      ...this.mapConnection(connectionRecord),
      invitation: invitationJson,
    };
  }

  @Post("/receive-invitation")
  async receiveInvitation(
    @BodyParams("data") invitation: Record<string, unknown>
  ) {
    const connection = await this.agent.connections.receiveInvitation(
      JsonTransformer.fromJSON(invitation, ConnectionInvitationMessage)
    );

    return this.mapConnection(connection);
  }

  @Post("/accept-invitation")
  async acceptInvitation(@BodyParams("id") connectionId: string) {
    const connection = await this.agent.connections.acceptInvitation(
      connectionId
    );

    return this.mapConnection(connection);
  }

  @Post("/accept-request")
  async acceptRequest(@BodyParams("id") connectionId: string) {
    await this.waitForState(connectionId, ConnectionState.Requested)

    const connection = await this.agent.connections.acceptRequest(connectionId);

    return this.mapConnection(connection);
  }

  @Post("/send-ping")
  async sendPing(
    @BodyParams("id") connectionId: string,
    // For now we ignore data. This could contain a comment property,
    // AFJ doesn't support passing it for now
    @BodyParams("data") data: any
  ) {
    await this.waitForState(connectionId, ConnectionState.Responded)
    const connection = await this.agent.connections.acceptResponse(
      connectionId
    );

    return this.mapConnection(connection);
  }

  private async waitForState(connectionId: string, state: ConnectionState) {
    // Wait for event that we have received the connection request
    // max waiting 20 seconds.
    return await firstValueFrom(this.subject.pipe(
      filter(c => c.payload.connectionRecord.id === connectionId),
      filter(c => c.payload.connectionRecord.state === ConnectionState.Requested),
      timeout(20000)
    ))
  }

  private mapConnection(connection: ConnectionRecord) {
    return {
      state: connection.state,
      connection_id: connection.id,
      connection,
    };
  }
}
