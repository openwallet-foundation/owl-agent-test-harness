
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
        public dynamic Data { get; set; }
    }
}