import { $log } from "@tsed/common";
import {
  Agent,
  HttpOutboundTransporter,
  InitConfig,
  LogLevel,
} from "@aries-framework/core";
import { agentDependencies, HttpInboundTransport } from "@aries-framework/node";

import { TsedLogger } from "./TsedLogger";

export async function createAgent({
  port,
  endpoint,
  publicDidSeed,
  genesisPath,
  agentName,
}: {
  port: number;
  endpoint: string;
  publicDidSeed: string;
  genesisPath: string;
  agentName: string;
}) {
  // TODO: Public did does not seem to be registered
  // TODO: Schema is prob already registered
  const agentConfig: InitConfig = {
    label: agentName,
    walletConfig: { id: `aath-javascript-${Date.now()}` },
    walletCredentials: { key: "00000000000000000000000000000Test01" },
    poolName: "aries-framework-javascript-pool",
    endpoint,
    publicDidSeed,
    genesisPath,
    logger: new TsedLogger($log),
  };

  const agent = new Agent(agentConfig, agentDependencies);

  agent.setInboundTransporter(new HttpInboundTransport({ port }));
  agent.setOutboundTransporter(new HttpOutboundTransporter());

  await agent.initialize();

  return agent;
}
