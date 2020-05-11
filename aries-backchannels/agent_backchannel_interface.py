
class AgentBackchannelInterface(agent_backchannel):
    """
    Interface for building Aries agent backchannel adapters for integration into the aries agent test harness.

    This interface extends agent_backchannel that already has some base infrasturcture and comms implmeneted to integrate with the test harness

    Extend this interface and implement hooks to communicate with a specific agent.
    """

    async def make_agent_POST_request(self, op, rec_id=None, data=None, text=False, params=None)-> (int, str):
        """Description."""
        pass

    async def make_agent_GET_request(self, op, rec_id=None, text=False, params=None) -> (int, str):
        """Description."""
        pass

