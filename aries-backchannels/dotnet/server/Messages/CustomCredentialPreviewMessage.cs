using Hyperledger.Aries.Agents;
using Hyperledger.Aries.Features.IssueCredential;
using Newtonsoft.Json;

namespace DotNet.Backchannel.Messages
{
    /// <summary>
    /// A credential content message.
    /// </summary>
    public class CustomCredentialPreviewMessage
    {
        /// <inheritdoc />
        public CustomCredentialPreviewMessage()
        {
            Type = MessageTypes.IssueCredentialNames.PreviewCredential;
        }

        /// <summary>
        ///  Gets or sets the type.
        /// </summary>
        /// <value></value>
        [JsonProperty("@type")]
        public string Type { get; set; }

        /// <summary>
        /// Gets or sets the attributes
        /// </summary>kk
        /// <value></value>
        [JsonProperty("attributes")]
        public CredentialPreviewAttribute[] Attributes { get; set; }
    }
}