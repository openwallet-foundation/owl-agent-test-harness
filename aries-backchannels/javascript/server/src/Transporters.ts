import { $log } from "@tsed/common";
import { Agent, InboundTransporter } from "aries-framework";
import type { Express } from "express";

export class HttpInboundTransporter implements InboundTransporter {
  private app: Express;

  public constructor(app: Express) {
    this.app = app;
  }

  public async start(agent: Agent) {
    this.app.post("/msg", async (req, res) => {
      const message = req.body;
      $log.info("received agent message", message);
      await agent.receiveMessage(message);
      // TODO: try/catch
      res.send(200);
    });
  }
}
