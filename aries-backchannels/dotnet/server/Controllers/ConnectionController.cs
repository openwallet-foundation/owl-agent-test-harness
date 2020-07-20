using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using DotNet.Backchannel.Models;

using Hyperledger.Aries.Features.DidExchange;
using Hyperledger.Aries.Features.TrustPing;
using Hyperledger.Aries.Agents;
using Hyperledger.Aries.Models.Events;
using Microsoft.Extensions.Caching.Memory;
using Hyperledger.Aries.Contracts;
using System.Reactive.Linq;
using System;

namespace DotNet.Backchannel.Controllers
{
    [Route("agent/command/connection")]
    [ApiController]
    public class ConnectionController : ControllerBase
    {
        private readonly IEventAggregator _eventAggregator;
        private readonly IConnectionService _connectionService;
        private readonly IAgentProvider _agentContextProvider;
        private readonly IMessageService _messageService;
        private IMemoryCache _connectionCache;

        public ConnectionController(
            IEventAggregator eventAggregator,
            IConnectionService connectionService,
            IAgentProvider agentContextProvider,
            IMessageService messageService,
            IMemoryCache memoryCache)
        {
            _eventAggregator = eventAggregator;
            _connectionService = connectionService;
            _agentContextProvider = agentContextProvider;
            _messageService = messageService;
            _connectionCache = memoryCache;
        }

        [HttpGet]
        public async Task<IActionResult> GetAllConnectionsAsync()
        {
            var context = await _agentContextProvider.GetContextAsync();
            var connections = await _connectionService.ListAsync(context);

            // TODO: Should we also return the invitation connections from the cache?
            return Ok(connections.ConvertAll(connection =>
            {

                var testHarnessConnection = _connectionCache.Get<TestHarnessConnection>(connection.Id);
                if (testHarnessConnection != null) return MapConnection(testHarnessConnection);

                return new
                {
                    connection_id = connection.Id,
                    state = connection.State
                };
            }));
        }

        [HttpGet("{connectionId}")]
        public async Task<IActionResult> GetConnectionByIdAsync([FromRoute] string connectionId)
        {
            var context = await _agentContextProvider.GetContextAsync();

            var testHarnessConnection = _connectionCache.Get<TestHarnessConnection>(connectionId);
            if (testHarnessConnection != null) return Ok(MapConnection(testHarnessConnection));

            var connection = await _connectionService.GetAsync(context, connectionId); // TODO: Handle AriesFrameworkException if connection not found
            return Ok(new
            {
                connection_id = connection.Id,
                state = connection.State
            });
        }

        [HttpPost("create-invitation")]
        public async Task<IActionResult> CreateInvitationAsync()
        {
            var context = await _agentContextProvider.GetContextAsync();

            var (invitation, connection) = await _connectionService.CreateInvitationAsync(context, new InviteConfiguration
            {
                MyAlias = new ConnectionAlias { Name = "dotnet" }
            });

            var testHarnessConnection = new TestHarnessConnection
            {
                ConnectionId = connection.Id,
                // State is 'Invited', should be 'invitation'
                State = TestHarnessConnectionState.Invitation
            };

            _connectionCache.Set(connection.Id, testHarnessConnection);

            // Listen for connection request to update the state
            UpdateStateOnMessage(testHarnessConnection, TestHarnessConnectionState.Request, _ => _.MessageType == MessageTypes.ConnectionRequest && _.RecordId == connection.Id);

            return Ok(new { connection_id = testHarnessConnection.ConnectionId, state = testHarnessConnection.State, invitation });
        }

        [HttpPost("receive-invitation")]
        public async Task<IActionResult> ReceiveInvitationAsync(OperationBody body)
        {

            var invitation = body.Data.ToObject<ConnectionInvitationMessage>();
            var context = await _agentContextProvider.GetContextAsync();

            var (request, record) = await _connectionService.CreateRequestAsync(context, invitation);

            var THConnection = new TestHarnessConnection
            {
                ConnectionId = record.Id,
                // State is 'Negotiation', should be 'invitation'
                State = TestHarnessConnectionState.Invitation,
                Request = request
            };

            // Cache is needed because the test harness separates
            // Receiving and accepting of invitations but .NET does not support that
            // We generate the ConnectionRequestMessage and store it in the cache.
            // It will be send in the accept-invitation operation.
            _connectionCache.Set(record.Id, THConnection);

            return Ok(MapConnection(THConnection));
        }

        [HttpPost("accept-invitation")]
        public async Task<IActionResult> AcceptInvitationAsync(OperationBody body)
        {
            var connectionId = body.Id;

            var testHarnessConnection = _connectionCache.Get<TestHarnessConnection>(connectionId);
            if (testHarnessConnection == null) return NotFound(); // Return early if not found

            var context = await _agentContextProvider.GetContextAsync();
            var connection = await _connectionService.GetAsync(context, connectionId); // TODO: Handle AriesFrameworkException if connection not found

            // Listen for connection response to update the state
            UpdateStateOnMessage(testHarnessConnection, TestHarnessConnectionState.Response, _ => _.MessageType == MessageTypes.ConnectionResponse && _.RecordId == connection.Id);

            await _messageService.SendAsync(context.Wallet, testHarnessConnection.Request, connection);

            // State is 'Negotiation', should be 'request'
            testHarnessConnection.State = TestHarnessConnectionState.Request;

            return Ok();
        }

        [HttpPost("accept-request")]
        public async Task<IActionResult> AcceptRequestAsync(OperationBody body)
        {
            var connectionId = body.Id;

            var testHarnessConnection = _connectionCache.Get<TestHarnessConnection>(connectionId);
            if (testHarnessConnection == null) return NotFound(); // Return early if not found

            var context = await _agentContextProvider.GetContextAsync();

            var (response, connection) = await _connectionService.CreateResponseAsync(context, connectionId);
            await _messageService.SendAsync(context.Wallet, response, connection);

            // State is 'Connected', should be 'response'
            testHarnessConnection.State = TestHarnessConnectionState.Response;

            return Ok();
        }

        [HttpPost("send-ping")]
        public async Task<IActionResult> SendPingAsync(OperationBody body)
        {
            var connectionId = body.Id;
            var data = body.Data;

            var testHarnessConnection = _connectionCache.Get<TestHarnessConnection>(connectionId);
            if (testHarnessConnection == null) return NotFound(); // Return early if not found

            var context = await _agentContextProvider.GetContextAsync();
            var connection = await _connectionService.GetAsync(context, connectionId); // TODO: Handle AriesFrameworkException if connection not found
            var message = new TrustPingMessage
            {
                Comment = (string)data["comment"]
            };
            await _messageService.SendAsync(context.Wallet, message, connection);

            // State is 'Connected', should be 'active'
            testHarnessConnection.State = TestHarnessConnectionState.Active;

            return Ok();
        }

        private object MapConnection(TestHarnessConnection THConnection) => new
        {
            connection_id = THConnection.ConnectionId,
            state = THConnection.State
        };

        private void UpdateStateOnMessage(TestHarnessConnection testHarnessConnection, TestHarnessConnectionState nextState, Func<ServiceMessageProcessingEvent, bool> predicate)
        {
            _eventAggregator.GetEventByType<ServiceMessageProcessingEvent>()
            .Where(predicate)
            .Take(1)
            .Subscribe(_ => { testHarnessConnection.State = nextState; });
        }
    }
}
