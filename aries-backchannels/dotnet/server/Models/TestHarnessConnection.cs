using System.Runtime.Serialization;
using Hyperledger.Aries.Features.Handshakes.DidExchange;
using Hyperledger.Aries.Features.Handshakes.Connection.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace DotNet.Backchannel.Models
{
    public enum TestHarnessConnectionState
    {
        [EnumMember(Value = "invited")]
        Invited,

        [EnumMember(Value = "requested")]
        Requested,

        [EnumMember(Value = "responded")]
        Responded,

        [EnumMember(Value = "complete")]
        Complete,
    }

    public class TestHarnessConnection
    {

        [JsonProperty("connection_id")]
        public string ConnectionId;

        [JsonProperty("state")]
        [JsonConverter(typeof(StringEnumConverter))]
        public TestHarnessConnectionState State;

        [JsonIgnore]
        public ConnectionRequestMessage Request;
    }
}