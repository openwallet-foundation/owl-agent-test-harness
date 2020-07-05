using DotNet.Backchannel.Utils;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Hosting;
using System;
using System.Diagnostics;
using System.Threading.Tasks;

namespace DotNet.Backchannel
{
    public class Program
    {
        /// <param name="p">Choose the starting port number to listen on</param>
        /// <param name="i">Start agent interactively</param>
        // TODO: Improve CLI argument handling / parsing
        public static void Main(int p, bool i)
        {
            // Catch all unhandled exceptions
            AppDomain.CurrentDomain.UnhandledException += new UnhandledExceptionEventHandler(CurrentDomain_UnhandledException);

            Program.SetEnvironment(p).Wait();
            CreateHostBuilder().Build().Run();
        }

        public static async Task SetEnvironment(int port)
        {
            var RUNMODE = Environment.GetEnvironmentVariable("RUNMODE");
            var DOCKER_HOST = Environment.GetEnvironmentVariable("DOCKER_HOST") ?? "host.docker.internal";
            var EXTERNAL_HOST = RUNMODE == "docker" ? DOCKER_HOST : "localhost";
            var LEDGER_URL = Environment.GetEnvironmentVariable("LEDGER_URL") ?? $"http://{EXTERNAL_HOST}:9000";
            var ENDPOINT_HOST = $"http://{EXTERNAL_HOST}:{port}";
            var GENESIS_PATH = await LedgerUtils.GetGenesisPathAsync();
            var ISSUER_KEY_SEED = LedgerUtils.getRandomSeed();

            await LedgerUtils.RegisterPublicDidAsync(LEDGER_URL, ISSUER_KEY_SEED, "dotnet-backchannel");

            Environment.SetEnvironmentVariable("ISSUER_KEY_SEED", ISSUER_KEY_SEED);
            Environment.SetEnvironmentVariable("ENDPOINT_HOST", ENDPOINT_HOST);
            Environment.SetEnvironmentVariable("DOCKER_HOST", DOCKER_HOST);
            Environment.SetEnvironmentVariable("GENESIS_PATH", GENESIS_PATH);
        }

        public static IHostBuilder CreateHostBuilder() => Host.CreateDefaultBuilder()
            .ConfigureWebHostDefaults(builder =>
            {
                builder.UseStartup<Startup>();
                builder.UseUrls(Environment.GetEnvironmentVariable("ENDPOINT_HOST"));
            });

        static void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            // Log the exception, display it, etc
            Debug.WriteLine((e.ExceptionObject as Exception).Message);
        }
    }
}
