using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Hosting;
using System;

namespace DotNet.Backchannel
{
    public class Program
    {
        /// <param name="p">Choose the starting port number to listen on</param>
        /// <param name="i">Start agent interactively</param>
        // TODO: Improve CLI argument handling / parsing
        public static void Main(int p, bool i)
        {
            Environment.SetEnvironmentVariable("ENDPOINT_HOST", $"http://0.0.0.0:{p}/");

            CreateHostBuilder(p).Build().Run();
        }

        public static IHostBuilder CreateHostBuilder(int port) => Host.CreateDefaultBuilder()
            .ConfigureWebHostDefaults(builder =>
            {
                builder.UseStartup<Startup>();
                builder.UseUrls($"http://0.0.0.0:{port}/");
            });
    }
}
