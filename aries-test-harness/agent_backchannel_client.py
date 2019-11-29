import asyncio
from aiohttp import (
    web,
    ClientSession,
    ClientRequest,
    ClientResponse,
    ClientError,
    ClientTimeout,
)


######################################################################
# coroutine utilities
######################################################################

def run_coroutine(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine())
    finally:
        loop.close()

def run_coroutine_with_args(coroutine, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine(*args))
    finally:
        loop.close()

def run_coroutine_with_kwargs(coroutine, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine(*args, **kwargs))
    finally:
        loop.close()


async def make_agent_backchannel_request(
    method, path, data=None, text=False, params=None
) -> (int, str):
    params = {k: v for (k, v) in (params or {}).items() if v is not None}
    client_session: ClientSession = ClientSession()
    async with client_session.request(
        method, path, json=data, params=params
    ) as resp:
        resp_status = resp.status
        resp_text = await resp.text()
        await client_session.close()
        return (resp_status, resp_text)


def agent_backchannel_GET(url, topic, operation=None, id=None, data=None) -> (int, str):
    agent_url = url + topic + "/"
    if id:
        agent_url = agent_url + id + "/"
    (resp_status, resp_text) = run_coroutine_with_kwargs(make_agent_backchannel_request, "GET", agent_url)
    return (resp_status, resp_text)


def agent_backchannel_POST(url, topic, operation=None, id=None, data=None) -> (int, str):
    agent_url = url + topic + "/"
    payload = {}
    if data:
        payload["data"] = data
    if operation:
        payload["operation"] = operation
    if id:
        payload["id"] = id
    (resp_status, resp_text) = run_coroutine_with_kwargs(make_agent_backchannel_request, "POST", agent_url, data=payload)
    return (resp_status, resp_text)

