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

        [HttpPost]
        public async Task<IActionResult> PresentProofOperationAsync(OperationBody body)
        {
            switch (body.Operation)
            {
                case "send-proposal":
                    return await this.SendPresentationProposalAsync(body.Id, body.Data);
                case "send-request":
                    // TODO: ID can be both pres_exchange_id OR connection_id
                    // Find out how this works exactly. Probably as different key
                    return await this.SendPresentationRequestAsync(body.Id, body.Data);
                case "send-presentation":
                    return await this.SendProofPresentationOfferAsync(body.Id, body.Data);
                case "verify-presentation":
                    return await this.VerifyPresentation(body.Id);
                default:
                    throw new NotSupportedException();
            }
        }

        private async Task<IActionResult> SendPresentationProposalAsync(string connectionId, dynamic proposal)
        {
            throw new NotImplementedException();
        }

        private async Task<IActionResult> SendPresentationRequestAsync(string proofRecordId, dynamic proofRequest)
        {
            throw new NotImplementedException();
        }

        private async Task<IActionResult> SendProofPresentationOfferAsync(string proofRecordId, dynamic proofPresentation)
        {
            throw new NotImplementedException();
        }

        private async Task<IActionResult> VerifyPresentation(string proofRecordId)
        {
            throw new NotImplementedException();
        }
    }
}
