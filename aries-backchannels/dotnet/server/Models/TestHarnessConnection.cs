using System.Runtime.Serialization;
using Hyperledger.Aries.Features.DidExchange;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace DotNet.Backchannel.Models
{
    public enum TestHarnessConnectionState
    {
        [EnumMember(Value = "invitation")]
        Invitation,

        [EnumMember(Value = "request")]
        Request,

        [EnumMember(Value = "response")]
        Response,

        [EnumMember(Value = "active")]
        Active,
    }

    public class TestHarnessConnection
    {

        public string ConnectionId;

        [JsonConverter(typeof(StringEnumConverter))]
        public TestHarnessConnectionState State;
        public ConnectionRequestMessage Request;
    }
}