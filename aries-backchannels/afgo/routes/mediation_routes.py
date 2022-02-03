import json
from typing import TYPE_CHECKING
from aiohttp import web

if TYPE_CHECKING:
    from afgo.afgo_backchannel import AfGoAgentBackchannel

routes = web.RouteTableDef()


@routes.get("/agent/command/mediation/{connection_id}")
async def get_mediation_record(request: web.Request):
    connection_id = request.match_info["connection_id"]
    backchannel: "AfGoAgentBackchannel" = request["backchannel"]

    # Not possible to determine the mediation state in most cases for AFGO
    state = "N/A"

    (resp_status, resp_text) = await backchannel.admin_GET("/mediator/connections")
    if resp_status != 200:
        return web.Response(text=resp_text, status=resp_status)

    # If connections includes connection id it means request was granted
    resp_json = json.loads(resp_text)
    if resp_json["connections"] and connection_id in resp_json["connections"]:
        state = "grant-received"

    return web.json_response({"connection_id": connection_id, "state": state})


@routes.post("/agent/command/mediation/send-request/")
async def mediation_send_request(request: web.Request):
    """Send mediate-request message to agent with specified connection id."""
    body = await request.json()
    connection_id: str = body.get("id")
    backchannel: "AfGoAgentBackchannel" = request["backchannel"]

    (resp_status, resp_text) = await backchannel.admin_POST(
        "/mediator/register", {"connectionID": connection_id}
    )

    if resp_status != 200:
        return web.Response(text=resp_text, status=resp_status)

    # If response was 200 state is request-sent
    return web.json_response({"connection_id": connection_id, "state": "request-sent"})


@routes.post("/agent/command/mediation/send-grant/")
async def mediation_send_grant(request: web.Request):
    body = await request.json()
    connection_id: str = body.get("id")

    # grant is automatically sent on AFGO side.
    # We assume the state is grant-sent. No way to determine what the state is
    return web.json_response({"connection_id": connection_id, "state": "grant-sent"})


@routes.post("/agent/command/mediation/send-deny/")
async def mediation_send_deny(_: web.Request):
    return web.HTTPNotImplemented(text="mediate-deny message not supported by AFGO.")
