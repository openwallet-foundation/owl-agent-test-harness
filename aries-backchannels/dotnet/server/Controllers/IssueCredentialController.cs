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

        [HttpPost("send-proposal")]
        public async Task<IActionResult> SendCredentialProposalAsync(OperationBody body)
        {
            var connectionId = body.Id;
            var proposal = body.Data;

            throw new NotImplementedException();
        }

        [HttpPost("send")]
        public async Task<IActionResult> SendCredentialAsync(OperationBody body)
        {
            var connectionId = body.Id;
            var credentialOffer = body.Data;

            throw new NotImplementedException();
        }

        [HttpPost("send-offer")]
        public async Task<IActionResult> SendCredentialOfferAsync(OperationBody body)
        {
            // TODO: ID can be both cred_exchange_id OR connection_id
            // Find out how this works exactly. Probably as different key
            var connectionId = body.Id;
            var credentialOffer = body.Data;

            throw new NotImplementedException();
        }

        [HttpPost("send-request")]
        public async Task<IActionResult> SendCredentialRequestAsync(OperationBody body)
        {
            var credentialRecordId = body.Id;

            throw new NotImplementedException();
        }

        [HttpPost("issue")]
        public async Task<IActionResult> IssueCredentialAsync(OperationBody body)
        {
            var credentialRecordId = body.Id;
            var credentialPreview = body.Data; // Can be undefined!

            throw new NotImplementedException();
        }

        [HttpPost("store")]
        public async Task<IActionResult> StoreCredentialAsync(OperationBody body)
        {
            var credentialRecordId = body.Id;

            throw new NotImplementedException();
        }
    }
}
