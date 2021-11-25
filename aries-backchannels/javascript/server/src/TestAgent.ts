import { $log } from '@tsed/common'
import { Agent, HttpOutboundTransport, InitConfig, WsOutboundTransport } from '@aries-framework/core'
import { agentDependencies, HttpInboundTransport } from '@aries-framework/node'

import { TsedLogger } from './TsedLogger'

export async function createAgent({
  port,
  endpoint,
  publicDidSeed,
  genesisPath,
  agentName,
  useLegacyDidSovPrefix,
}: {
  port: number
  endpoint: string
  publicDidSeed: string
  genesisPath: string
  agentName: string
  useLegacyDidSovPrefix: boolean
}) {
  // TODO: Public did does not seem to be registered
  // TODO: Schema is prob already registered
  $log.level = 'debug'

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
    endpoints: [endpoint],
    publicDidSeed,
    useLegacyDidSovPrefix,
    logger: new TsedLogger($log),
  }

  const agent = new Agent(agentConfig, agentDependencies)

  agent.registerInboundTransport(new HttpInboundTransport({ port }))
  agent.registerOutboundTransport(new HttpOutboundTransport())
  agent.registerOutboundTransport(new WsOutboundTransport())

  await agent.initialize()

  return agent
}
