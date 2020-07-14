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
            CreateHostBuilder(p).Build().Run();
        }

        public static async Task SetEnvironment(int port)
        {
            var DOCKER_HOST = Environment.GetEnvironmentVariable("DOCKERHOST") ?? "host.docker.internal";
            var EXTERNAL_HOST = DOCKER_HOST;
            var LEDGER_URL = Environment.GetEnvironmentVariable("LEDGER_URL") ?? $"http://{EXTERNAL_HOST}:9000";
            var ENDPOINT_HOST = $"http://{EXTERNAL_HOST}:{port}";
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
