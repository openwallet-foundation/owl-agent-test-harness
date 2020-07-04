using System;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using DotNet.Backchannel.Models;

using Hyperledger.Aries.Features.DidExchange;
using Hyperledger.Aries.Features.TrustPing;
using Hyperledger.Aries.Agents;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command/connection")]
    [ApiController]
    public class ConnectionController : ControllerBase
    {
        private readonly IConnectionService _connectionService;
        private readonly IAgentProvider _agentContextProvider;
        private readonly IMessageService _messageService;

        public ConnectionController(
            IConnectionService connectionService,
            IAgentProvider agentContextProvider,
            IMessageService messageService)
        {
            _connectionService = connectionService;
            _agentContextProvider = agentContextProvider;
            _messageService = messageService;

        }

        [HttpGet]
        public async Task<IActionResult> GetAllConnectionsAsync()
        {
            throw new NotImplementedException();
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetConnectionByIdAsync([FromRoute] string id)
        {
            throw new NotImplementedException();
        }

        [HttpPost]
        public async Task<IActionResult> ConnectionOperationAsync(OperationBody body)
        {
            switch (body.Operation)
            {
                case "create-invitation":
                    return await this.CreateInvitationAsync();
                case "receive-invitation":
                    return await this.ReceiveInvitationAsync(body.Data);
                case "accept-invitation":
                    return await this.AcceptInvitationAsync(body.Id);
                case "accept-request":
                    return await this.AcceptRequestAsync(body.Id);
                case "send-ping":
                    return await this.SendPingAsync(body.Id, body.Data);
                default:
                    throw new NotSupportedException();
            }
        }

        private async Task<IActionResult> CreateInvitationAsync()
        {
            var context = await _agentContextProvider.GetContextAsync();

            var (invitation, connection) = await _connectionService.CreateInvitationAsync(context, new InviteConfiguration());

            return StatusCode(200, new { connection_id = connection.Id, invitation });
        }

        private async Task<IActionResult> ReceiveInvitationAsync(object invitation)
        {
            throw new NotImplementedException();
        }

        private async Task<IActionResult> AcceptInvitationAsync(string connectionId)
        {
            throw new NotImplementedException();
        }

        private async Task<IActionResult> AcceptRequestAsync(string connectionId)
        {
            throw new NotImplementedException();
        }
        private async Task<IActionResult> SendPingAsync(string connectionId, dynamic data)
        {
            var context = await _agentContextProvider.GetContextAsync();
            var connection = await _connectionService.GetAsync(context, connectionId);
            var message = new TrustPingMessage
            {
                ResponseRequested = true,
                Comment = data.comment
            };

            await _messageService.SendAsync(context.Wallet, message, connection);

            return StatusCode(200);
        }
    }
}
