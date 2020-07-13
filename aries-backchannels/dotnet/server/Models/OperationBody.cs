using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace DotNet.Backchannel.Models
{
    public class OperationBody
    {
        [JsonProperty(PropertyName = "operation")]
        public string Operation { get; set; }

        [JsonProperty(PropertyName = "id")]
        public string Id { get; set; }

        [JsonProperty(PropertyName = "data")]
        public JObject Data { get; set; }
    }
}