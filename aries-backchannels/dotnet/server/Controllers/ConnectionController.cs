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

            return Ok(connections.ConvertAll(connection => _connectionCache.Get<TestHarnessConnection>(connection.Id)));
        }

        [HttpGet("{connectionId}")]
        public async Task<IActionResult> GetConnectionByIdAsync([FromRoute] string connectionId)
        {
            var context = await _agentContextProvider.GetContextAsync();

            try
            {
                var THConnection = _connectionCache.Get<TestHarnessConnection>(connectionId);
                var connection = await _connectionService.GetAsync(context, connectionId);
                if (THConnection == null) return NotFound();

                return Ok(THConnection);
            }
            catch
            {
                // Connection record not found
                return NotFound();
            }


        }

        [HttpPost("create-invitation")]
        public async Task<IActionResult> CreateInvitationAsync()
        {
            var context = await _agentContextProvider.GetContextAsync();

            var (invitation, connection) = await _connectionService.CreateInvitationAsync(context);

            var testHarnessConnection = new TestHarnessConnection
            {
                ConnectionId = connection.Id,
                State = TestHarnessConnectionState.Invited
            };

            _connectionCache.Set(connection.Id, testHarnessConnection);

            // Listen for connection request to update the state
            UpdateStateOnMessage(testHarnessConnection, TestHarnessConnectionState.Requested, _ => _.MessageType == MessageTypes.ConnectionRequest && _.RecordId == connection.Id);

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
                State = TestHarnessConnectionState.Invited,
                Request = request
            };

            _connectionCache.Set(record.Id, THConnection);

            return Ok(THConnection);
        }

        [HttpPost("accept-invitation")]
        public async Task<IActionResult> AcceptInvitationAsync(OperationBody body)
        {
            var connectionId = body.Id;
            var context = await _agentContextProvider.GetContextAsync();

            var THConnection = _connectionCache.Get<TestHarnessConnection>(connectionId);
            if (THConnection == null) return NotFound(); // Return early if not found

            ConnectionRecord connection;
            try { connection = await _connectionService.GetAsync(context, connectionId); }
            catch { return NotFound(); }

            // Listen for connection response to update the state
            UpdateStateOnMessage(THConnection, TestHarnessConnectionState.Responded, _ => _.MessageType == MessageTypes.ConnectionResponse && _.RecordId == connection.Id);

            await _messageService.SendAsync(context, THConnection.Request, connection);

            THConnection.State = TestHarnessConnectionState.Requested;

            return Ok(THConnection);


        }

        [HttpPost("accept-request")]
        public async Task<IActionResult> AcceptRequestAsync(OperationBody body)
        {
            var connectionId = body.Id;
            var context = await _agentContextProvider.GetContextAsync();

            var THConnection = _connectionCache.Get<TestHarnessConnection>(connectionId);
            if (THConnection == null) return NotFound(); // Return early if not found

            var (response, connection) = await _connectionService.CreateResponseAsync(context, connectionId);
            await _messageService.SendAsync(context, response, connection);

            THConnection.State = TestHarnessConnectionState.Responded;

            return Ok(THConnection);
        }

        [HttpPost("send-ping")]
        public async Task<IActionResult> SendPingAsync(OperationBody body)
        {
            var connectionId = body.Id;
            var data = body.Data;
            var context = await _agentContextProvider.GetContextAsync();

            var THConnection = _connectionCache.Get<TestHarnessConnection>(connectionId);
            if (THConnection == null) return NotFound(); // Return early if not found

            ConnectionRecord connection;
            try { connection = await _connectionService.GetAsync(context, connectionId); }
            catch { return NotFound(); }

            var message = new TrustPingMessage
            {
                Comment = (string)data["comment"]
            };
            await _messageService.SendAsync(context, message, connection);

            THConnection.State = TestHarnessConnectionState.Complete;

            return Ok(THConnection);
        }

        private void UpdateStateOnMessage(TestHarnessConnection THConnection, TestHarnessConnectionState nextState, Func<ServiceMessageProcessingEvent, bool> predicate)
        {
            _eventAggregator.GetEventByType<ServiceMessageProcessingEvent>()
            .Where(predicate)
            .Take(1)
            .Subscribe(_ => { THConnection.State = nextState; });
        }
    }
}
