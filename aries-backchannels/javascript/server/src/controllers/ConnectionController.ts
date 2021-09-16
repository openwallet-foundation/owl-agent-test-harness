import { Controller, Get, PathParams, Post, BodyParams } from "@tsed/common";
import { NotFound } from "@tsed/exceptions";
import {
  Agent,
  ConnectionRecord,
  ConnectionInvitationMessage,
  JsonTransformer,
} from "@aries-framework/core";

@Controller("/agent/command/connection")
export class ConnectionController {
  private agent: Agent;

  public constructor(agent: Agent) {
    this.agent = agent;
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

    return {
      ...this.mapConnection(connectionRecord),
      invitation: invitation.toJSON(),
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
    await new Promise(f => setTimeout(f, 5000));
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
    const connection = await this.agent.connections.acceptResponse(
      connectionId
    );

    return this.mapConnection(connection);
  }

  private mapConnection(connection: ConnectionRecord) {
    return {
      state: connection.state,
      connection_id: connection.id,
      connection,
    };
  }
}
