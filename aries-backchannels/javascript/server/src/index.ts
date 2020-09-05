import { $log } from "@tsed/common";
import { PlatformExpress } from "@tsed/platform-express";
import { registerProvider } from "@tsed/di";
import { createAgent } from "./TestAgent";
import { Server } from "./Server";
import { Agent } from "aries-framework-javascript";
import minimist from "minimist";

async function bootstrap() {
  const cliArguments = minimist(process.argv.slice(2), {
    alias: {
      port: "p",
    },
    default: {
      port: 9020,
    },
  });

  const backchannelPort = Number(cliArguments.port);
  const agentPort = backchannelPort + 1;
  const dockerHost = process.env.DOCKERHOST ?? "host.docker.internal";
  const runMode = process.env.RUN_MODE;
  const externalHost = runMode === "docker" ? dockerHost : "localhost";
  const ledgerUrl = process.env.LEDGER_URL ?? `http://${externalHost}:9000`;
  const endpointUrl = `http://${externalHost}`;

  const agent = await createAgent({
    url: endpointUrl,
    port: agentPort,
  });

  registerProvider({
    provide: Agent,
    useValue: agent,
  });

  try {
    $log.debug("Start server...");
    const platform = await PlatformExpress.bootstrap(Server);

    platform.settings.port = cliArguments.port;

    await platform.listen();
    $log.debug("Server initialized");
  } catch (er) {
    $log.error(er);
  }
}

bootstrap();
