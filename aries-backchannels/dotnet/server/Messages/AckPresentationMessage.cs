using System;
using Hyperledger.Aries.Agents;
using Newtonsoft.Json;

namespace DotNet.Backchannel.Messages
{

    /// <summary>
    /// Ack Presentation Message
    /// </summary>
    public class AckPresentationMessage : AgentMessage
    {
        /// <summary>
        /// Initializes a new instance of <see cref="AckPresentationMessage"/> class.
        /// </summary>
        public AckPresentationMessage()
        {
            Id = Guid.NewGuid().ToString();
            Type = CustomMessageTypes.AckPresentation;
        }

        /// <summary>
        /// Gets or sets the comment.
        /// </summary>
        /// <value>
        /// The comment.
        /// </value>
        [JsonProperty("status")]
        public string Status { get; set; }
    }
}