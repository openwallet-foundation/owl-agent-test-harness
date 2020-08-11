using System.Runtime.Serialization;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace DotNet.Backchannel.Models
{
    public enum TestHarnessPresentationExchangeState
    {
        [EnumMember(Value = "proposal-sent")]
        ProposalSent,

        [EnumMember(Value = "proposal-received")]
        ProposalReceived,

        [EnumMember(Value = "request-sent")]
        RequestSent,

        [EnumMember(Value = "request-received")]
        RequestReceived,

        [EnumMember(Value = "presentation-sent")]
        PresentationSent,

        [EnumMember(Value = "presentation-received")]
        PresentationReceived,

        [EnumMember(Value = "reject-sent")]
        RejectSent,

        [EnumMember(Value = "done")]
        Done,
    }

    public class TestHarnessPresentationExchange
    {

        [JsonProperty("thread_id")]
        public string ThreadId;

        [JsonIgnore]
        public string RecordId;

        [JsonProperty("state")]
        [JsonConverter(typeof(StringEnumConverter))]
        public TestHarnessPresentationExchangeState State;
    }
}