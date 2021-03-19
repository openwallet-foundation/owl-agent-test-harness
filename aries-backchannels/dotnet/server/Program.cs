using DotNet.Backchannel.Utils;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Hosting;
using System;
using System.Diagnostics;
using System.Threading.Tasks;
using System.CommandLine;
using System.CommandLine.Invocation;

namespace DotNet.Backchannel
{
    public class Program
    {
        public static async Task<int> Main(params string[] args)
        {
            // Catch all unhandled exceptions
            AppDomain.CurrentDomain.UnhandledException += new UnhandledExceptionEventHandler(CurrentDomain_UnhandledException);

            RootCommand rootCommand = new RootCommand(
                description: "Start an .NET agent with backchannel"
            ) {
             new Option<int>(
                new string[] { "--port", "-p" },
                // When debugging with VSCode we can't pass the -p argument.
                getDefaultValue: () => Int32.Parse(Environment.GetEnvironmentVariable("BACKCHANNEL_PORT") ?? "9020")
            ) {
                IsRequired = false
            },

             new Option<bool>(
                new string[] { "--interactive", "-i" },
                getDefaultValue: () => false
            ) {
                IsRequired = false
            }
            };

            rootCommand.Handler = CommandHandler.Create<int, bool>((port, interactive) =>
            {
                Program.SetEnvironment(port).Wait();
                LogUtils.EnableIndyLogging();
                CreateHostBuilder(port).Build().Run();
            });

            return await rootCommand.InvokeAsync(args);
        }

        public static async Task SetEnvironment(int port)
        {
            var DOCKER_HOST = Environment.GetEnvironmentVariable("DOCKERHOST") ?? "host.docker.internal";
            var EXTERNAL_HOST = DOCKER_HOST;
            var LEDGER_URL = Environment.GetEnvironmentVariable("LEDGER_URL") ?? $"http://{EXTERNAL_HOST}:9000";
            var ENDPOINT_HOST = Environment.GetEnvironmentVariable("AGENT_PUBLIC_ENDPOINT") ?? $"http://{EXTERNAL_HOST}:{port}";
            var ISSUER_KEY_SEED = LedgerUtils.getRandomSeed();
            var GENESIS_URL = Environment.GetEnvironmentVariable("GENESIS_URL");
            var GENESIS_FILE = Environment.GetEnvironmentVariable("GENESIS_FILE");
            var GENESIS_PATH = await LedgerUtils.GetGenesisPathAsync(GENESIS_FILE, GENESIS_URL, LEDGER_URL, DOCKER_HOST);

            await LedgerUtils.RegisterPublicDidAsync(LEDGER_URL, ISSUER_KEY_SEED, "dotnet-backchannel");

            Environment.SetEnvironmentVariable("ISSUER_KEY_SEED", ISSUER_KEY_SEED);
            Environment.SetEnvironmentVariable("ENDPOINT_HOST", ENDPOINT_HOST);
            Environment.SetEnvironmentVariable("GENESIS_PATH", GENESIS_PATH);
        }

        public static IHostBuilder CreateHostBuilder(int port) => Host.CreateDefaultBuilder()
            .ConfigureWebHostDefaults(builder =>
            {
                builder.UseStartup<Startup>();
                builder.UseUrls($"http://0.0.0.0:{port}");
            });

        static void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            // Log the exception, display it, etc
            Debug.WriteLine((e.ExceptionObject as Exception).Message);
        }
    }
}
