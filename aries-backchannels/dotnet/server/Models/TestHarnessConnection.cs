using System.Runtime.Serialization;
using Hyperledger.Aries.Features.DidExchange;
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

        public string ConnectionId;

        [JsonConverter(typeof(StringEnumConverter))]
        public TestHarnessConnectionState State;
        public ConnectionRequestMessage Request;
    }
}