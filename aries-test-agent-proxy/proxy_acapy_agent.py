import asyncio
import asyncpg
import functools
import json
import logging
import os
import random
import subprocess
import sys
from timeit import default_timer

from aiohttp import (
    web,
    ClientSession,
    ClientRequest,
    ClientResponse,
    ClientError,
    ClientTimeout,
)

from proxy_agent import ProxyAgent, default_genesis_txns, RUN_MODE, START_TIMEOUT
from utils import require_indy, flatten, log_json, log_msg, log_timer, output_reader, prompt_loop


LOGGER = logging.getLogger(__name__)

DEFAULT_BIN_PATH = "../venv/bin"
DEFAULT_PYTHON_PATH = ".."

if RUN_MODE == "docker":
    DEFAULT_BIN_PATH = "./bin"
    DEFAULT_PYTHON_PATH = "."
elif RUN_MODE == "pwd":
    DEFAULT_BIN_PATH = "./bin"
    DEFAULT_PYTHON_PATH = "."

class ProxyAcaPyAgent(ProxyAgent):
    def __init__(
        self, 
        ident: str,
        http_port: int,
        admin_port: int,
        genesis_data: str = None,
        params: dict = {}
    ):
        super().__init__(
            ident,
            http_port,
            admin_port,
            genesis_data,
            params
        )

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

    async def make_agent_GET_request(
        self, op, rec_id=None, text=False, params=None
    ) -> (int, str):
        if op["topic"] == "connection":
            if rec_id:
                connection_id = rec_id
                agent_operation = "/connections/" + connection_id
            else:
                agent_operation = "/connections"
            
            (resp_status, resp_text) = await self.admin_GET(agent_operation)

            return (resp_status, resp_text)

        return (404, '404: Not Found\n\n'.encode('utf8'))

    async def make_agent_POST_request(
        self, op, rec_id=None, data=None, text=False, params=None
    ) -> (int, str):
        if op["topic"] == "connection":
            operation = op["operation"]
            if (operation == "create-invitation" 
                or operation == "receive-invitation"
            ):
                agent_operation = "/connections/" + operation

                (resp_status, resp_text) = await self.admin_POST(agent_operation, data=data)

                return (resp_status, resp_text)

            elif (operation == "accept-connection" 
                or operation == "accept-request"
                or operation == "remove"
                or operation == "start-introduction"
                or operation == "send-ping"
            ):
                connection_id = rec_id
                agent_operation = "/connections/" + operation + "/" + connection_id

                (resp_status, resp_text) = await self.admin_POST(agent_operation, data)

                return (resp_status, resp_text)

        return (404, '404: Not Found\n\n'.encode('utf8'))

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
        agent = ProxyAcaPyAgent(
            "aca-py", start_port+1, start_port+2, genesis_data=genesis
        )

        # start backchannel (common across all types of agents)
        await agent.listen_backchannel(start_port)

        # start aca-py agent sub-process and listen for web hooks
        await agent.listen_webhooks(start_port+3)
        await agent.register_did()

        await agent.start_process()

        # now wait ...
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
