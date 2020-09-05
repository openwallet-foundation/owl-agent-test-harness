import {
  OutboundTransporter,
  OutboundPackage,
  InboundTransporter,
  Agent,
} from "aries-framework-javascript";
import { Express } from "express";

export class HttpOutboundTransporter implements OutboundTransporter {
  public async sendMessage(
    outboundPackage: OutboundPackage,
    receiveReply: boolean
  ) {
    const { payload, endpoint } = outboundPackage;

    if (!endpoint) {
      throw new Error(
        `Missing endpoint. I don't know how and where to send the message.`
      );
    }

    const response = await fetch(endpoint, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (receiveReply) {
      return JSON.parse(await response.text());
    }
  }
}

export class HttpInboundTransporter implements InboundTransporter {
  private app: Express;

  public constructor(app: Express) {
    this.app = app;
  }

  public start(agent: Agent) {
    this.app.post("/msg", async (req, res) => {
      const message = req.body;
      const packedMessage = JSON.parse(message);
      const outboundMessage = await agent.receiveMessage(packedMessage);
      if (outboundMessage) {
        res.status(200).json(outboundMessage.payload).end();
      } else {
        res.status(200).end();
      }
    });
  }
}
