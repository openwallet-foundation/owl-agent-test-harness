import { $log } from '@tsed/common'
import { Agent, InitConfig, MediatorPickupStrategy } from '@aries-framework/core'
import { agentDependencies } from '@aries-framework/node'

import { TsedLogger } from './TsedLogger'
import { TransportConfig } from './TestHarnessConfig'

export async function createAgent({
  publicDidSeed,
  genesisPath,
  agentName,
  transport,
}: {
  publicDidSeed: string
  genesisPath: string
  agentName: string
  transport: TransportConfig
}) {
  // TODO: Public did does not seem to be registered
  // TODO: Schema is prob already registered

  const agentConfig: InitConfig = {
    label: agentName,
    walletConfig: {
      id: `aath-javascript-${Date.now()}`,
      key: '00000000000000000000000000000Test01',
    },
    indyLedgers: [
      {
        id: 'main-pool',
        isProduction: false,
        genesisPath,
      },
    ],
    endpoints: transport.endpoints,
    publicDidSeed,
    // Needed to accept mediation requests: https://github.com/hyperledger/aries-framework-javascript/issues/668
    autoAcceptMediationRequests: true,
    useLegacyDidSovPrefix: true,
    logger: new TsedLogger($log),
  }

  const agent = new Agent(agentConfig, agentDependencies)

  for (const it of transport.inboundTransports) {
    agent.registerInboundTransport(it)
  }

  for (const ot of transport.outboundTransports) {
    agent.registerOutboundTransport(ot)
  }

  await agent.initialize()

  return agent
}
