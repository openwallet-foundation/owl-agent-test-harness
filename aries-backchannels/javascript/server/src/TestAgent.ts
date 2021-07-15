import { $log } from "@tsed/common";
import {
  Agent,
  DidCommMimeType,
  HttpOutboundTransporter,
  InitConfig,
  LogLevel,
} from "aries-framework";
import { NodeFileSystem } from "aries-framework/build/src/storage/fs/NodeFileSystem";
import express from "express";
import indy from "indy-sdk";
import { HttpInboundTransporter } from "./Transporters";
import { TsedLogger } from "./TsedLogger";

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
  // TODO: Public did does not seem to be registered
  // TODO: Schema is prob already registered
  const agentConfig: InitConfig = {
    label: "javascript",
    walletConfig: { id: `aath-javascript-${Date.now()}` },
    walletCredentials: { key: "00000000000000000000000000000Test01" },
    fileSystem: new NodeFileSystem(),
    poolName: "aries-framework-javascript-pool",
    host: url,
    port,
    publicDidSeed,
    genesisPath,
    indy,
    logger: new TsedLogger({
      logLevel: LogLevel.debug,
      logger: $log,
      name: "TestHarness",
    }),
  };

  const agent = new Agent(agentConfig);

  const app = express();
  app.use(
    express.json({
      type: [DidCommMimeType.V0, DidCommMimeType.V1],
    })
  );

  const inboundTransporter = new HttpInboundTransporter(app);

  agent.setInboundTransporter(inboundTransporter);
  agent.setOutboundTransporter(new HttpOutboundTransporter(agent));

  await agent.initialize();

  app.listen(port, async () => {
    inboundTransporter.start(agent);
    $log.info(`Agent listening on port ${url}:${port}`);
  });

  return agent;
}
