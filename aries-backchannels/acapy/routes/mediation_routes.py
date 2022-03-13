import asyncio
import json
from time import sleep
from typing import Any, Dict, TYPE_CHECKING
from aiohttp import web

if TYPE_CHECKING:
    from acapy.acapy_backchannel import AcaPyAgentBackchannel


routes = web.RouteTableDef()


def response_state_from_mediation_record(record: Dict[str, Any]):
    """Maps from acapy mediation role and state to AATH state"""
    state = record["state"]

    mediator_states = {
        "request": "request-received",
        "granted": "grant-sent",
        "denied": "deny-sent",
    }

    recipient_states = {
        "request": "request-sent",
        "granted": "grant-received",
        "denied": "deny-received",
    }

    # recipient
    if record["role"] == "client":
        return recipient_states[state]
    # mediator
    else:
        return mediator_states[state]


def mediation_record_to_response(record: Dict[str, Any]):
    state = response_state_from_mediation_record(record)
    return {"connection_id": record["connection_id"], "state": state}


async def get_mediation_record_by_connection_id(
    backchannel: "AcaPyAgentBackchannel", connection_id: str
):
    (_, resp_text) = await backchannel.admin_GET(
        "/mediation/requests", params={"conn_id": connection_id}
    )

    resp_json = json.loads(resp_text)

    if len(resp_json["results"]) == 0:
        raise web.HTTPNotFound(
            reason=f"No mediation record found for connection with id {connection_id}"
        )

    # Should not be possible. ACA-Py only allows one mediation record set-up per connection
    if len(resp_json["results"]) > 1:
        raise web.HTTPConflict(
            reason=f"Multiple mediation records found for connection with id {connection_id}"
        )

    return resp_json["results"][0]


@routes.get("/agent/command/mediation/{connection_id}")
async def get_mediation_record(request: web.Request):
    connection_id: str = request.match_info["connection_id"]
    backchannel: "AcaPyAgentBackchannel" = request["backchannel"]

    mediation_record = await get_mediation_record_by_connection_id(
        backchannel, connection_id
    )

    return web.json_response(mediation_record_to_response(mediation_record))


@routes.post("/agent/command/mediation/send-request/")
async def mediation_send_request(request: web.Request):
    """Send mediate-request message to agent with specified connection id."""
    body = await request.json()
    connection_id: str = body.get("id")
    backchannel: "AcaPyAgentBackchannel" = request["backchannel"]

    (resp_status, resp_text) = await backchannel.admin_POST(
        f"/mediation/request/{connection_id}", {}
    )

    if resp_status != 201:
        return web.Response(text=resp_text, status=resp_status)

    resp_json = json.loads(resp_text)
    return web.json_response(mediation_record_to_response(resp_json))


@routes.post("/agent/command/mediation/send-grant/")
async def mediation_send_grant(request: web.Request):
    body = await request.json()
    connection_id: str = body.get("id")
    backchannel: "AcaPyAgentBackchannel" = request["backchannel"]

    # This seems to need a sleep to work
    await asyncio.sleep(2)

    mediation_record = await get_mediation_record_by_connection_id(
        backchannel, connection_id
    )

    # Auto accept is enabled, so we're not granting the mediation explicitly
    return web.json_response(mediation_record_to_response(mediation_record))


@routes.post("/agent/command/mediation/send-deny/")
async def mediation_send_deny(request: web.Request):
    body = await request.json()
    connection_id: str = body.get("id")
    backchannel: "AcaPyAgentBackchannel" = request["backchannel"]

    # This seems to need a sleep to work
    sleep(2)

    mediation_record = await get_mediation_record_by_connection_id(
        backchannel, connection_id
    )
    mediation_id = mediation_record["mediation_id"]

    (resp_status, resp_text) = await backchannel.admin_POST(
        f"/mediation/requests/{mediation_id}/deny", {}
    )

    if resp_status != 201:
        return web.Response(text=resp_text, status=resp_status)

    resp_json = json.loads(resp_text)
    return web.json_response(mediation_record_to_response(resp_json))
