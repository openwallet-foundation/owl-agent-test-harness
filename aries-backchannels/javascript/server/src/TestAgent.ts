// @ts-ignore
import indy from "indy-sdk";
import { InitConfig, Agent } from "aries-framework-javascript";
import express from "express";
import * as bodyParser from "body-parser";
import {
  HttpInboundTransporter,
  HttpOutboundTransporter,
} from "./Transporters";
import { $log } from "@tsed/common";

export async function createAgent({
  port,
  url,
}: {
  port: number;
  url: string;
}) {
  const agentConfig: InitConfig = {
    label: "javascript",
    walletConfig: { id: `aath-javascript-${Date.now()}` },
    walletCredentials: { key: "00000000000000000000000000000Test01" },
    url,
    port,
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

  await agent.init();

  app.listen(port, async () => {
    inboundTransporter.start(agent);
    $log.info(`Agent listening on port ${url}:${port}`);
  });

  return agent;
}
