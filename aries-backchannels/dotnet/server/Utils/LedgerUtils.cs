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


        public static async Task RegisterPublicDidAsync(string ledgerUrl, string seed, string alias = null)
        {
            var data = new
            {
                alias,
                seed,
                role = "TRUST_ANCHOR"
            };

            var json = JsonConvert.SerializeObject(data);
            var stringContent = new StringContent(json, UnicodeEncoding.UTF8, MediaTypeNames.Application.Json);

            var requestUrl = ledgerUrl + "/register";
            await LedgerUtils.Client.PostAsync(requestUrl, stringContent);
        }

        public static string getRandomSeed()
        {
            Random random = new Random();
            String randomNum = random.Next(100000, 999999).ToString();

            String seed = $"my_seed_000000000000000000{randomNum}";

            return seed;
        }

        public static async Task<string> GetGenesisPathAsync(string genesisFile = null, string genesisUrl = null, string ledgerUrl = null, string dockerHost = null)
        {
            // If the genesis file is present, we already have the path
            if (genesisFile != null) return genesisFile;

            string genesisTransactionUrl = null;

            if (genesisUrl != null) genesisTransactionUrl = genesisUrl;
            else if (ledgerUrl != null) genesisTransactionUrl = $"{ledgerUrl}/genesis";
            else genesisTransactionUrl = $"http://{dockerHost}:9000/genesis";

            var result = await LedgerUtils.Client.GetAsync(genesisTransactionUrl);

            var genesis = await result.Content.ReadAsStringAsync();
            var genesisPath = Path.GetTempFileName();
            File.WriteAllText(genesisPath, genesis);

            return genesisPath;
        }
    }
}