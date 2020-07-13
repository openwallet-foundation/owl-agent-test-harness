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

        [HttpPost("create-invitation")]
        public async Task<IActionResult> CreateInvitationAsync()
        {
            var context = await _agentContextProvider.GetContextAsync();

            var (invitation, connection) = await _connectionService.CreateInvitationAsync(context, new InviteConfiguration());

            return Ok(new { connection_id = connection.Id, invitation });
        }

        [HttpPost("receive-invitation")]
        public async Task<IActionResult> ReceiveInvitationAsync(OperationBody body)
        {
            var invitationBody = body.Data;
            throw new NotImplementedException();
        }

        [HttpPost("accept-invitation")]
        public async Task<IActionResult> AcceptInvitationAsync(OperationBody body)
        {
            var connectionId = body.Id;
            throw new NotImplementedException();
        }

        [HttpPost("accept-request")]
        public async Task<IActionResult> AcceptRequestAsync(OperationBody body)
        {
            var connectionId = body.Id;
            throw new NotImplementedException();
        }

        [HttpPost("send-ping")]
        public async Task<IActionResult> SendPingAsync(OperationBody body)
        {
            var connectionId = body.Id;
            var data = body.Data;

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
