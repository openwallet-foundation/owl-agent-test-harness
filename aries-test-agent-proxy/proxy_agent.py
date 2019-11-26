import asyncio
import asyncpg
import functools
import json
import logging
import os
import random
import subprocess
import sys
import prompt_toolkit
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.eventloop.defaults import use_asyncio_event_loop
from prompt_toolkit.patch_stdout import patch_stdout
from timeit import default_timer

import pygments
from pygments.filter import Filter
from pygments.lexer import Lexer
from pygments.lexers.data import JsonLdLexer
from prompt_toolkit.formatted_text import FormattedText, PygmentsTokens

from aiohttp import (
    web,
    ClientSession,
    ClientRequest,
    ClientResponse,
    ClientError,
    ClientTimeout,
)

from utils import require_indy, flatten, log_json, log_msg, log_timer, output_reader, prompt_loop


LOGGER = logging.getLogger(__name__)

DEFAULT_POSTGRES = bool(os.getenv("POSTGRES"))
DEFAULT_INTERNAL_HOST = "127.0.0.1"
DEFAULT_EXTERNAL_HOST = "localhost"
DEFAULT_BIN_PATH = "./venv/bin"
DEFAULT_PYTHON_PATH = ".."

START_TIMEOUT = float(os.getenv("START_TIMEOUT", 30.0))

RUN_MODE = os.getenv("RUNMODE")

GENESIS_URL = os.getenv("GENESIS_URL")
LEDGER_URL = os.getenv("LEDGER_URL")

if RUN_MODE == "docker":
    DEFAULT_INTERNAL_HOST = os.getenv("DOCKERHOST") or "host.docker.internal"
    DEFAULT_EXTERNAL_HOST = DEFAULT_INTERNAL_HOST
    DEFAULT_BIN_PATH = "./bin"
    DEFAULT_PYTHON_PATH = "."
elif RUN_MODE == "pwd":
    # DEFAULT_INTERNAL_HOST =
    DEFAULT_EXTERNAL_HOST = os.getenv("DOCKERHOST") or "host.docker.internal"
    DEFAULT_BIN_PATH = "./bin"
    DEFAULT_PYTHON_PATH = "."


async def default_genesis_txns():
    genesis = None
    try:
        if GENESIS_URL:
            async with ClientSession() as session:
                async with session.get(GENESIS_URL) as resp:
                    genesis = await resp.text()
        elif RUN_MODE == "docker":
            async with ClientSession() as session:
                async with session.get(
                    f"http://{DEFAULT_EXTERNAL_HOST}:9000/genesis"
                ) as resp:
                    genesis = await resp.text()
        else:
            with open("local-genesis.txt", "r") as genesis_file:
                genesis = genesis_file.read()
    except Exception:
        LOGGER.exception("Error loading genesis transactions:")
    return genesis


class ProxyAgent:
    def __init__(
        self, 
        ident: str,
        http_port: int,
        admin_port: int,
        genesis_data: str = None,
        params: dict = {}
    ):
        self.ident = ident
        self.http_port = http_port
        self.admin_port = admin_port
        self.genesis_data = genesis_data
        self.params = params
        rand_name = str(random.randint(100_000, 999_999))
        self.seed = ("my_seed_000000000000000000000000" + rand_name)[-32:]

        self.internal_host = DEFAULT_INTERNAL_HOST
        self.external_host = DEFAULT_EXTERNAL_HOST
        self.label = ident

        if RUN_MODE == "pwd":
            self.endpoint = f"http://{self.external_host}".replace(
                "{PORT}", str(http_port)
            )
        else:
            self.endpoint = f"http://{self.external_host}:{http_port}"
        self.admin_url = f"http://{self.internal_host}:{admin_port}"

        self.storage_type = "indy"
        self.wallet_type = "indy"
        self.wallet_name = self.ident.lower().replace(" ", "") + rand_name
        self.wallet_key = self.ident + rand_name
        self.did = None
        self.postgres = False

        self.client_session: ClientSession = ClientSession()

    async def listen_backchannel(self, backchannel_port):
        """ 
        Setup the routes to allow the test harness to send commands to and get replies
        from the Agent under test.

        Expected topics include:

            schema                 GET to return a list and POST to create/update
            credential-definition  GET to return a list and POST to create/update
            message                POST to send message
            connection             GET to return a list or single; POST to create/update*
            credential             GET to return a list or single; POST to create/update*
            proof                  GET to return a list or single; POST to create/update*

        GET with no parameters returns all
        GET with an "id" parameter will return a single record
        POST will submit a JSON payload
        POST* will contain an "operation" element within the payload to define the operation
        POST operations on existing records must contain an "id" element
        POST operations will contain a "data" element which is the payload to pass through to the agent

        Operations for each topic are:

            connection    create-invitation, receive-invitation, accept-connection, accept-request, remove, start-introduction, send-ping
            credential    send-offer, send-request, issue, problem-report, remove
            proof         send-request, send-proposal, send-presentation, verify-presentation, remove

        E.g.:  POST to /agent/command/issue_credential { "operation":"send-proposal", "data":"{...}"}
        E.g.:  POST to /agent/command/issue_credential { "operation":"issue", "id":"<cred exch id>", "data":"{...}"}
        """
        app = web.Application()
        app.add_routes([web.post("/agent/command/{topic}/", self._post_command_backchannel)])
        app.add_routes([web.get("/agent/command/{topic}/", self._get_command_backchannel)])
        app.add_routes([web.get("/agent/command/{topic}/{id}", self._get_command_backchannel)])
        app.add_routes([web.get("/agent/response/{topic}/", self._get_response_backchannel)])
        app.add_routes([web.get("/agent/response/{topic}/{id}", self._get_response_backchannel)])
        app.add_routes([web.post("/agent/reply/{topic}/", self._post_reply_backchannel)])
        runner = web.AppRunner(app)
        await runner.setup()
        self.backchannel_site = web.TCPSite(runner, "0.0.0.0", backchannel_port)
        await self.backchannel_site.start()
        print("Listening to backchannel on port", backchannel_port)

    async def _post_command_backchannel(self, request: ClientRequest):
        """
        Post a POST command to the agent.
        """
        topic = request.match_info["topic"]
        payload = await request.json()

        if topic == "connection" and "operation" in payload and "data" in payload:
            operation = payload["operation"]
            data = payload["data"]
            if (operation == "create-invitation" 
                or operation == "receive-invitation"
            ):
                agent_operation = "/connections/" + operation
                (resp_status, resp_text) = await self.admin_POST(agent_operation, data)

                return web.Response(text=resp_text, status=resp_status)

            elif (operation == "accept-connection" 
                or operation == "accept-request"
                or operation == "remove"
                or operation == "start-introduction"
                or operation == "send-ping"
            ) and "id" in payload:
                connection_id = payload["id"]
                agent_operation = "/connections/" + operation + "/" + connection_id
                (resp_status, resp_text) = await self.admin_POST(agent_operation, data)

                return web.Response(text=resp_text, status=resp_status)

        return web.Response(body='404: Not Found\n\n'.encode('utf8'), status=404)

    async def _get_command_backchannel(self, request: ClientRequest):
        """
        Post a GET command to the agent.
        """
        topic = request.match_info["topic"]

        if topic == "connection":
            if "id" in request.match_info:
                connection_id = request.match_info["id"]
                agent_operation = "/connections/" + connection_id
            else:
                agent_operation = "/connections"
            (resp_status, resp_text) = await self.admin_GET(agent_operation)
            
            return web.Response(text=resp_text, status=resp_status)

        return web.Response(body='404: Not Found\n\n'.encode('utf8'), status=404)

    async def _get_response_backchannel(self, request: ClientRequest):
        """
        Get a response from the (remote) agent.
        """
        return web.Response(text="")

    async def _post_reply_backchannel(self, request: ClientRequest):
        """
        Reply to a response from the (remote) agent.
        """
        return web.Response(text="")

    async def listen_webhooks(self, webhook_port):
        self.webhook_port = webhook_port
        if RUN_MODE == "pwd":
            self.webhook_url = f"http://localhost:{str(webhook_port)}/webhooks"
        else:
            self.webhook_url = (
                f"http://{self.external_host}:{str(webhook_port)}/webhooks"
            )
        app = web.Application()
        app.add_routes([web.post("/webhooks/topic/{topic}/", self._receive_webhook)])
        runner = web.AppRunner(app)
        await runner.setup()
        self.webhook_site = web.TCPSite(runner, "0.0.0.0", webhook_port)
        await self.webhook_site.start()
        print("Listening to web_hooks on port", webhook_port)

    async def _receive_webhook(self, request: ClientRequest):
        topic = request.match_info["topic"]
        payload = await request.json()
        await self.handle_webhook(topic, payload)
        return web.Response(text="")

    async def handle_webhook(self, topic: str, payload):
        if topic != "webhook":  # would recurse
            handler = f"handle_{topic}"
            method = getattr(self, handler, None)
            if method:
                await method(payload)
            else:
                log_msg(
                    f"Error: agent {self.ident} "
                    f"has no method {handler} "
                    f"to handle webhook on topic {topic}"
                )

    async def make_admin_request(
        self, method, path, data=None, text=False, params=None
    ) -> (int, str):
        params = {k: v for (k, v) in (params or {}).items() if v is not None}
        async with self.client_session.request(
            method, self.admin_url + path, json=data, params=params
        ) as resp:
            resp_status = resp.status
            resp_text = await resp.text()
            return (resp_status, resp_text)

    async def admin_GET(self, path, text=False, params=None) -> (int, str):
        try:
            return await self.make_admin_request("GET", path, None, text, params)
        except ClientError as e:
            self.log(f"Error during GET {path}: {str(e)}")
            raise

    async def admin_POST(
        self, path, data=None, text=False, params=None
    ) -> (int, str):
        try:
            return await self.make_admin_request("POST", path, data, text, params)
        except ClientError as e:
            self.log(f"Error during POST {path}: {str(e)}")
            raise

    def log(self, msg):
        print(msg)

    def handle_output(self, *output, source: str = None, **kwargs):
        end = "" if source else "\n"
        if source == "stderr":
            color = "fg:ansired"
        elif not source:
            color = self.color or "fg:ansiblue"
        else:
            color = None
        log_msg(*output, color=color, prefix=self.prefix_str, end=end, **kwargs)

    async def register_did(self, ledger_url: str = None, alias: str = None):
        if not ledger_url:
            ledger_url = LEDGER_URL
        if not ledger_url:
            ledger_url = f"http://{self.external_host}:9000"
        data = {"alias": alias or self.ident, "seed": self.seed, "role": "TRUST_ANCHOR"}
        async with self.client_session.post(
            ledger_url + "/register", json=data
        ) as resp:
            if resp.status != 200:
                raise Exception(f"Error registering DID, response code {resp.status}")
            nym_info = await resp.json()
            self.did = nym_info["did"]
        self.log(f"Got DID: {self.did}")

    def get_agent_args(self):
        result = [
            ("--endpoint", self.endpoint),
            ("--label", self.label),
            "--auto-ping-connection",
            "--auto-respond-messages",
            ("--inbound-transport", "http", "0.0.0.0", str(self.http_port)),
            ("--outbound-transport", "http"),
            ("--admin", "0.0.0.0", str(self.admin_port)),
            "--admin-insecure-mode",
            ("--wallet-type", self.wallet_type),
            ("--wallet-name", self.wallet_name),
            ("--wallet-key", self.wallet_key),
        ]
        if self.genesis_data:
            result.append(("--genesis-transactions", self.genesis_data))
        if self.seed:
            result.append(("--seed", self.seed))
        if self.storage_type:
            result.append(("--storage-type", self.storage_type))
        if self.postgres:
            result.extend(
                [
                    ("--wallet-storage-type", "postgres_storage"),
                    ("--wallet-storage-config", json.dumps(self.postgres_config)),
                    ("--wallet-storage-creds", json.dumps(self.postgres_creds)),
                ]
            )
        if self.webhook_url:
            result.append(("--webhook-url", self.webhook_url))
        #if self.extra_args:
        #    result.extend(self.extra_args)

        return result

    def _process(self, args, env, loop):
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            encoding="utf-8",
        )
        loop.run_in_executor(
            None,
            output_reader,
            proc.stdout,
            functools.partial(self.handle_output, source="stdout"),
        )
        loop.run_in_executor(
            None,
            output_reader,
            proc.stderr,
            functools.partial(self.handle_output, source="stderr"),
        )
        return proc

    def get_process_args(self, bin_path: str = None):
        cmd_path = "aca-py"
        if bin_path is None:
            bin_path = DEFAULT_BIN_PATH
        if bin_path:
            cmd_path = os.path.join(bin_path, cmd_path)
        return list(flatten((["python3", cmd_path, "start"], self.get_agent_args())))

    async def detect_process(self):
        text = None

        async def fetch_swagger(url: str, timeout: float):
            text = None
            start = default_timer()
            async with ClientSession(timeout=ClientTimeout(total=3.0)) as session:
                while default_timer() - start < timeout:
                    try:
                        async with session.get(url) as resp:
                            if resp.status == 200:
                                text = await resp.text()
                                break
                    except (ClientError, asyncio.TimeoutError):
                        pass
                    await asyncio.sleep(0.5)
            return text

        swagger_url = self.admin_url + "/api/docs/swagger.json"
        text = await fetch_swagger(swagger_url, START_TIMEOUT)
        print("Agent running with admin url", self.admin_url)

        if not text:
            raise Exception(
                "Timed out waiting for agent process to start. "
                + f"Admin URL: {swagger_url}"
            )
        if "Aries Cloud Agent" not in text:
            raise Exception(
                f"Unexpected response from agent process. Admin URL: {swagger_url}"
            )

    async def start_process(
        self, python_path: str = None, bin_path: str = None, wait: bool = True
    ):
        my_env = os.environ.copy()
        python_path = DEFAULT_PYTHON_PATH if python_path is None else python_path
        if python_path:
            my_env["PYTHONPATH"] = python_path

        agent_args = self.get_process_args(bin_path)

        # start agent sub-process
        self.log(f"Starting agent sub-process ...")
        loop = asyncio.get_event_loop()
        self.proc = await loop.run_in_executor(
            None, self._process, agent_args, my_env, loop
        )
        if wait:
            await asyncio.sleep(1.0)
            await self.detect_process()

    def _terminate(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=0.5)
                self.log(f"Exited with return code {self.proc.returncode}")
            except subprocess.TimeoutExpired:
                msg = "Process did not terminate in time"
                self.log(msg)
                raise Exception(msg)

    async def terminate(self):
        loop = asyncio.get_event_loop()
        if self.proc:
            await loop.run_in_executor(None, self._terminate)
        await self.client_session.close()
        if self.webhook_site:
            await self.webhook_site.stop()


async def main(start_port: int, show_timing: bool = False):

    genesis = await default_genesis_txns()
    if not genesis:
        print("Error retrieving ledger genesis transactions")
        sys.exit(1)

    agent = None

    try:
        agent = ProxyAgent(
            "aca-py", start_port+1, start_port+2, genesis_data=genesis
        )
        await agent.listen_backchannel(start_port)
        await agent.listen_webhooks(start_port+3)
        await agent.register_did()

        await agent.start_process()

        async for option in prompt_loop(
            "(X) Exit? [X] "
        ):
            if option is None or option in "xX":
                break

    finally:
        terminated = True
        try:
            if agent:
                await agent.terminate()
        except Exception:
            LOGGER.exception("Error terminating agent:")
            terminated = False

    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Runs a Faber demo agent.")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8020,
        metavar=("<port>"),
        help="Choose the starting port number to listen on",
    )
    args = parser.parse_args()

    require_indy()

    try:
        asyncio.get_event_loop().run_until_complete(main(args.port))
    except KeyboardInterrupt:
        os._exit(1)

