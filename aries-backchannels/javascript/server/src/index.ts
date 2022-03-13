import { $log, registerProvider } from '@tsed/common'
import minimist from 'minimist'
import indy from 'indy-sdk'

import { TestHarnessConfig } from './TestHarnessConfig'
import { PlatformExpress } from '@tsed/platform-express'
import { Server } from './Server'

async function startup() {
  const cliArguments = minimist(process.argv.slice(2), {
    alias: {
      port: 'p',
    },
    default: {
      port: 9020,
    },
  })

  const testHarnessConfig = new TestHarnessConfig({ backchannelPort: Number(cliArguments.port) })

  registerProvider({
    provide: TestHarnessConfig,
    useValue: testHarnessConfig,
  })

  $log.level = 'debug'

  // @ts-ignore
  indy.setLogger(function (
    level: string,
    target: string,
    message: string,
    modulePath: string,
    file: string,
    line: string
  ) {
    console.log('libindy said:', level, target, message, modulePath, file, line)
  })

  // @ts-ignore
  indy.setRuntimeConfig({ collect_backtrace: true })

  await testHarnessConfig.startAgent({ inboundTransports: ['http'], outboundTransports: ['http'] })

  try {
    $log.debug('Start server...')
    const platform = await PlatformExpress.bootstrap(Server)

    platform.settings.port = testHarnessConfig.backchannelPort

    await testHarnessConfig.agentStartup()

    await platform.listen()

    $log.level = 'debug'
  } catch (er) {
    $log.error(er)

    throw er
  }
}

startup()
