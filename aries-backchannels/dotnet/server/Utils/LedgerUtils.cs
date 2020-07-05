using System;
using System.IO;
using System.Net.Http;
using System.Net.Mime;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace DotNet.Backchannel.Utils
{
    public static class LedgerUtils
    {
        private static HttpClient Client = new HttpClient();

        public static async Task<string> GetGenesisPathAsync()
        {
            String genesisPath = null;

            var RUN_MODE = Environment.GetEnvironmentVariable("RUNMODE");
            var GENESIS_URL = Environment.GetEnvironmentVariable("GENESIS_URL");
            var GENESIS_FILE = Environment.GetEnvironmentVariable("GENESIS_FILE");
            var LEDGER_URL = Environment.GetEnvironmentVariable("LEDGER_URL");
            var DOCKER_HOST = Environment.GetEnvironmentVariable("DOCKER_HOST") ?? "host.docker.internal";

            if (GENESIS_FILE != null) genesisPath = GENESIS_FILE;
            else if (LEDGER_URL != null || GENESIS_URL != null || RUN_MODE == "docker")
            {
                String genesisUrl = null;

                if (GENESIS_URL != null) genesisUrl = GENESIS_URL;
                else if (LEDGER_URL != null) genesisUrl = $"{LEDGER_URL}/genesis";
                else if (RUN_MODE == "docker") genesisUrl = $"http://{DOCKER_HOST}:9000/genesis";

                var result = await LedgerUtils.Client.GetAsync(genesisUrl);

                var genesis = await result.Content.ReadAsStringAsync();
                genesisPath = Path.GetFullPath("genesis.txn");
                File.WriteAllText(genesisPath, genesis);
            }
            else
            {
                // Use local file. Uses localhost instead of docker host for von-network
                genesisPath = Path.GetFullPath("../../data/local-genesis.txt");
            }

            return genesisPath;
        }
    }
}