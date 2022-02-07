from typing import TYPE_CHECKING, List, Optional
from aiohttp import web

from typing_extensions import TypedDict, Literal

if TYPE_CHECKING:
    from acapy.acapy_backchannel import AcaPyAgentBackchannel


routes = web.RouteTableDef()


class AgentStartParameters(TypedDict):
    inbound_transports: Optional[List[Literal["http", "ws"]]]
    outbound_transports: Optional[List[Literal["http", "ws"]]]


@routes.post("/agent/command/agent/start/")
async def get_mediation_record(request: web.Request):
    body = await request.json()
    backchannel: "AcaPyAgentBackchannel" = request["backchannel"]
    parameters: AgentStartParameters = body.get("data", {}).get("parameters", {})

    # Get agent host args. If inbound / outbound transports is not provided we use http by default
    # If an empty array is provided it means we don't want to use any transport
    # Useful for testing agents without endpoint
    inbound: List[str] = parameters.get("inbound_transports", ["http"])
    outbound: List[str] = parameters.get("outbound_transports", ["http"])

    args = backchannel.get_host_args(
        inbound_transports=inbound,
        outbound_transports=outbound,
    )

    await backchannel.kill_agent()
    await backchannel.start_process_with_extra_args(args=args)

    return web.json_response({})
