using System;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using DotNet.Backchannel.Models;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command/proof")]
    [ApiController]
    public class PresentProofController : ControllerBase
    {
        [HttpGet("{id}")]
        public async Task<IActionResult> GetProofRecordByIdAsync([FromRoute] string proofRecordId)
        {
            throw new NotImplementedException();
        }

        [HttpPost("send-proposal")]
        public async Task<IActionResult> SendPresentationProposalAsync(OperationBody body)
        {
            var connectionId = body.Id;
            var proposal = body.Data;

            throw new NotImplementedException();
        }

        [HttpPost("send-request")]
        public async Task<IActionResult> SendPresentationRequestAsync(OperationBody body)
        {
            // TODO: ID can be both pres_exchange_id OR connection_id
            // Find out how this works exactly. Probably as different key
            var proofRecordId = body.Id;
            var proofRequest = body.Data;

            throw new NotImplementedException();
        }

        [HttpPost("send-presentation")]
        public async Task<IActionResult> SendProofPresentationOfferAsync(OperationBody body)
        {
            var proofRecordId = body.Id;
            var proofPresentation = body.Data;

            throw new NotImplementedException();
        }

        [HttpPost("verify-presentation")]
        public async Task<IActionResult> VerifyPresentation(OperationBody body)
        {
            var proofRecordId = body.Id;

            throw new NotImplementedException();
        }
    }
}
