using System.Runtime.Serialization;
using Hyperledger.Aries.Features.IssueCredential;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace DotNet.Backchannel.Models
{
    public enum TestHarnessCredentialExchangeState
    {
        [EnumMember(Value = "proposal-sent")]
        ProposalSent,

        [EnumMember(Value = "proposal-received")]
        ProposalReceived,

        [EnumMember(Value = "offer-sent")]
        OfferSent,

        [EnumMember(Value = "offer-received")]
        OfferReceived,

        [EnumMember(Value = "request-sent")]
        RequestSent,

        [EnumMember(Value = "request-received")]
        RequestReceived,

        [EnumMember(Value = "credential-issued")]
        CredentialIssued,

        [EnumMember(Value = "credential-received")]
        CredentialReceived,

        [EnumMember(Value = "done")]
        Done,
    }

    public class TestHarnessCredentialExchange
    {

        [JsonProperty("thread_id")]
        public string ThreadId;


        [JsonProperty("credential_id", NullValueHandling = NullValueHandling.Ignore)]
        public string RecordId;

        [JsonProperty("state")]
        [JsonConverter(typeof(StringEnumConverter))]
        public TestHarnessCredentialExchangeState State;
    }
}