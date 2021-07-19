import { $log } from "@tsed/common";
import {
  Agent,
  DidCommMimeType,
  HttpOutboundTransporter,
  InitConfig,
  LogLevel,
} from "@aries-framework/core";
import { agentDependencies } from "@aries-framework/node";

import { HttpInboundTransporter } from "./Transporters";
import { TsedLogger } from "./TsedLogger";

export async function createAgent({
  port,
  endpoint,
  publicDidSeed,
  genesisPath,
}: {
  port: number;
  endpoint: string;
  publicDidSeed: string;
  genesisPath: string;
}) {
  // TODO: Public did does not seem to be registered
  // TODO: Schema is prob already registered
  const agentConfig: InitConfig = {
    label: "Aries Framework JavaScript",
    walletConfig: { id: `aath-javascript-${Date.now()}` },
    walletCredentials: { key: "00000000000000000000000000000Test01" },
    poolName: "aries-framework-javascript-pool",
    endpoint,
    publicDidSeed,
    genesisPath,
    logger: new TsedLogger({
      logLevel: LogLevel.debug,
      logger: $log,
      name: "TestHarness",
    }),
  };

  const agent = new Agent(agentConfig, agentDependencies);

  agent.setInboundTransporter(
    new HttpInboundTransporter({
      port,
    })
  );
  agent.setOutboundTransporter(new HttpOutboundTransporter());

  await agent.initialize();

  return agent;
}
