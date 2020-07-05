
using System.Text.Json;
using Newtonsoft.Json;

namespace DotNet.Backchannel.Models
{
    public class OperationBody
    {
        [JsonProperty(PropertyName = "operation")]
        public string Operation { get; set; }

        [JsonProperty(PropertyName = "id")]
        public string Id { get; set; }

        [JsonProperty(PropertyName = "data")]
        public JsonElement Data { get; set; }
    }
}