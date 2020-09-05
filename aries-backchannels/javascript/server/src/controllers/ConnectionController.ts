import { Controller, Get, Inject, PathParams, $log, Post } from "@tsed/common";
import { NotFound } from "@tsed/exceptions";
import { Agent, ConnectionRecord } from "aries-framework-javascript";

import { AGENT } from "../Symbols";

@Controller("/agent/command/connection")
export class ConnectionController {
  public constructor(@Inject(AGENT) private agent: Agent) {}

  @Get("/:connectionId")
  async getConnectionById(@PathParams("connectionId") connectionId: string) {
    const connection = await this.agent.connections.find(connectionId);

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
    const connection = await this.agent.connections.createConnection();

    return {
      ...this.mapConnection(connection),
      invitation: connection.invitation?.toJSON(),
    };
  }

  private mapConnection(connection: ConnectionRecord) {
    return {
      state: connection.state.toLowerCase(),
      connection_id: connection.id,
    };
  }
}
