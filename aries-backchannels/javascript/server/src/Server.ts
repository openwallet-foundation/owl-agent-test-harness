import { Configuration, Inject } from "@tsed/di";
import { PlatformApplication } from "@tsed/common";
import "@tsed/platform-express"; // /!\ keep this import
import * as bodyParser from "body-parser";
export const rootDir = __dirname;

@Configuration({
  rootDir,
  acceptMimes: ["application/json"],
  httpsPort: false,
  mount: {
    "/": [`${rootDir}/controllers/**/*.ts`],
  },
})
export class Server {
  @Inject()
  app!: PlatformApplication;

  @Configuration()
  settings!: Configuration;

  $beforeRoutesInit() {
    this.app.use(bodyParser.json());

    return null;
  }
}
