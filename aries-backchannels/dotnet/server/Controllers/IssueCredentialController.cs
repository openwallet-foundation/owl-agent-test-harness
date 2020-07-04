using System;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using DotNet.Backchannel.Models;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command/issue-credential")]
    [ApiController]
    public class IssueCredentialController : ControllerBase
    {
        [HttpGet("{id}")]
        public async Task<IActionResult> GetCredentialRecordByIdAsync([FromRoute] string credentialRecordId)
        {
            throw new NotImplementedException();
        }

        [HttpPost]
        public async Task<IActionResult> IssueCredentialOperationAsync(OperationBody body)
        {
            switch (body.Operation)
            {
                case "send-proposal":
                    return await this.SendCredentialProposalAsync(body.Id, body.Data);
                case "send":
                    return await this.SendCredentialAsync(body.Id, body.Data);
                case "send-offer":
                    // TODO: ID can be both cred_exchange_id OR connection_id
                    // Find out how this works exactly. Probably as different key
                    return await this.SendCredentialOfferAsync(body.Id, body.Data);
                case "send-request":
                    return await this.SendCredentialRequestAsync(body.Id);
                case "issue":
                    return await this.IssueCredentialAsync(body.Id, body.Data);
                case "store":
                    return await this.StoreCredentialAsync(body.Id, body.Data);
                default:
                    throw new NotSupportedException();
            }
        }

        private async Task<IActionResult> SendCredentialProposalAsync(string connectionId, dynamic proposal)
        {
            throw new NotImplementedException();
        }

        private async Task<IActionResult> SendCredentialAsync(string connectionId, dynamic credentialOffer)
        {
            throw new NotImplementedException();
        }

        private async Task<IActionResult> SendCredentialOfferAsync(string connectionId, dynamic credentialOffer)
        {
            throw new NotImplementedException();
        }

        private async Task<IActionResult> SendCredentialRequestAsync(string credentialRecordId)
        {
            throw new NotImplementedException();
        }

        private async Task<IActionResult> IssueCredentialAsync(string credentialRecordId, dynamic credentialOffer = null)
        {
            throw new NotImplementedException();
        }

        private async Task<IActionResult> StoreCredentialAsync(string credentialRecordId, dynamic credentialOffer = null)
        {
            throw new NotImplementedException();
        }
    }
}
