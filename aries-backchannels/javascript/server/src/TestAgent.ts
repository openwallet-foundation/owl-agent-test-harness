import indy from "indy-sdk";
import { InitConfig, Agent } from "aries-framework-javascript";
import express from "express";
import { $log } from "@tsed/common";

import {
  HttpInboundTransporter,
  HttpOutboundTransporter,
} from "./Transporters";

export async function createAgent({
  port,
  url,
  publicDidSeed,
  genesisPath,
}: {
  port: number;
  url: string;
  publicDidSeed: string;
  genesisPath: string;
}) {
  const agentConfig: InitConfig = {
    label: "javascript",
    walletConfig: { id: `aath-javascript-${Date.now()}` },
    walletCredentials: { key: "00000000000000000000000000000Test01" },
    publicDidSeed,
    host: url,
    port,
    poolName: "aries-framework-javascript-pool",
    genesisPath,
  };

  const app = express();
  app.use(
    express.json({
      type: "application/ssi-agent-wire",
    })
  );

  const inboundTransporter = new HttpInboundTransporter(app);
  const outboundTransporter = new HttpOutboundTransporter();

  const agent = new Agent(
    agentConfig,
    inboundTransporter,
    outboundTransporter,
    indy
  );

  await agent.init();

  app.listen(port, async () => {
    inboundTransporter.start(agent);
    $log.info(`Agent listening on port ${url}:${port}`);
  });

  return agent;
}
