using System;
using System.IO;
using Hyperledger.Aries.Storage;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

namespace DotNet.Backchannel
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            services.AddControllers()
            // Aries Framework .NET uses Newtonsoft JSON library
            .AddNewtonsoftJson();

            services.AddLogging();

            services.AddAriesFramework(builder =>
            {
                builder.RegisterAgent<DotNet.Backchannel.TestAgent>(c =>
                {
                    c.AgentName = Environment.GetEnvironmentVariable("AGENT_NAME");
                    c.EndpointUri = Environment.GetEnvironmentVariable("ENDPOINT_HOST");
                    c.WalletConfiguration = new WalletConfiguration { Id = "TestAgentWallet" };
                    c.WalletCredentials = new WalletCredentials { Key = "MyWalletKey" };
                    c.GenesisFilename = Environment.GetEnvironmentVariable("GENESIS_PATH");
                    c.IssuerKeySeed = Environment.GetEnvironmentVariable("ISSUER_KEY_SEED");
                });
            });
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }

            // Register agent middleware
            app.UseAriesFramework();

            app.UseRouting();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
            });
        }
    }
}
