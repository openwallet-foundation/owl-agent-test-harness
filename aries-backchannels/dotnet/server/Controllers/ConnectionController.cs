using System;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using DotNet.Backchannel.Models;
using Newtonsoft.Json.Linq;

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
            var context = await _agentContextProvider.GetContextAsync();
            var connections = await _connectionService.ListAsync(context);

            return Ok(connections.ConvertAll(connection =>
            {
                // TODO: states do not match states from RFC
                var state = connection.State == ConnectionState.Invited ? "invitation" : "TODO";

                return new
                {
                    connection_id = connection.Id,
                    state,
                    connection = connection
                };
            }

                ));
        }

        [HttpGet("{connectionId}")]
        public async Task<IActionResult> GetConnectionByIdAsync([FromRoute] string connectionId)
        {
            var context = await _agentContextProvider.GetContextAsync();
            var connection = await _connectionService.GetAsync(context, connectionId);
            // TODO: states do not match states from RFC
            var state = connection.State == ConnectionState.Invited ? "invitation" : "TODO";

            return Ok(new
            {
                connection_id = connection.Id,
                state,
                connection
            });
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

            return Ok(new { connection_id = connection.Id, invitation });
        }

        private async Task<IActionResult> ReceiveInvitationAsync(JObject invitationObject)
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
        private async Task<IActionResult> SendPingAsync(string connectionId, JObject data)
        {
            var context = await _agentContextProvider.GetContextAsync();
            var connection = await _connectionService.GetAsync(context, connectionId);
            var message = new TrustPingMessage
            {
                ResponseRequested = true,
                Comment = (string)data["comment"]
            };

            await _messageService.SendAsync(context.Wallet, message, connection);

            return Ok();
        }
    }
}
