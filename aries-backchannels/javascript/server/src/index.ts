import { $log } from "@tsed/common";
import { PlatformExpress } from "@tsed/platform-express";
import { registerProvider } from "@tsed/di";
import express from "express";
import bodyParser from "body-parser";
import { Agent, InitConfig } from "aries-framework-javascript";
// @ts-ignore
import indy from "indy-sdk";

import { Server } from "./Server";
import { AGENT } from "./Symbols";
import {
  HttpInboundTransporter,
  HttpOutboundTransporter,
} from "./Transporters";

async function bootstrap() {
  const agentConfig: InitConfig = {
    label: "javascript",
    walletConfig: { id: "e2e-alice" },
    walletCredentials: { key: "00000000000000000000000000000Test01" },
    url: "http://localhost",
    port: 9021,
  };

  const app = express();
  app.use(bodyParser.text());
  const inboundTransporter = new HttpInboundTransporter(app);
  const outboundTransporter = new HttpOutboundTransporter();

  const agent = new Agent(
    agentConfig,
    inboundTransporter,
    outboundTransporter,
    indy
  );

  registerProvider({
    provide: AGENT,
    useValue: agent,
  });

  app.listen(9021, async () => {
    await agent.init();
    inboundTransporter.start(agent);
    $log.info("Agent listening on port http://0.0.0.0:9021");
  });

  try {
    $log.debug("Start server...");
    const platform = await PlatformExpress.bootstrap(Server);

    await platform.listen();
    $log.debug("Server initialized");
  } catch (er) {
    $log.error(er);
  }
}

bootstrap();
