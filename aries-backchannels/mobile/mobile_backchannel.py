import asyncio
import base64
import json
import logging
import os

from time import sleep
from typing import Tuple

from qrcode import QRCode

from python.agent_backchannel import (
    AgentBackchannel,
    BackchannelCommand,
    RUN_MODE,
    AgentPorts,
)
from python.utils import (
    log_msg,
    prompt_loop,
)
from python.storage import (
    pop_resource,
)

LOGGER = logging.getLogger(__name__)

MAX_TIMEOUT = 5

DEFAULT_BIN_PATH = "../venv/bin"
DEFAULT_PYTHON_PATH = ".."

if RUN_MODE == "docker":
    DEFAULT_BIN_PATH = "./bin"
    DEFAULT_PYTHON_PATH = "."
elif RUN_MODE == "pwd":
    DEFAULT_BIN_PATH = "./bin"
    DEFAULT_PYTHON_PATH = "."


class MobileAgentBackchannel(AgentBackchannel):
    def __init__(
        self,
        ident: str,
        agent_ports: AgentPorts,
        genesis_data: str = None,
        params: dict = {},
    ):
        super().__init__(ident, agent_ports, genesis_data, params)
        self.connection_state = "n/a"

    async def make_agent_POST_request(
        self,
        command: BackchannelCommand,
    ) -> Tuple[int, str]:
        print("make_agent_POST_request:", command)

        operation = command.operation
        data = command.data
        record_id = command.record_id

        if command.topic == "connection":
            if operation == "receive-invitation":
                self.connection_state = "invited"
                print(
                    "================================================================="
                )

                message_bytes = json.dumps(data).encode("ascii")
                base64_bytes = base64.b64encode(message_bytes)
                base64_message = base64_bytes.decode("ascii")
                invitation_url = data["serviceEndpoint"] + "?c_i=" + base64_message

                qr = QRCode(border=1)
                qr.add_data(invitation_url)
                log_msg(
                    "Use the following JSON to accept the invite from another demo agent."
                    " Or use the QR code to connect from a mobile agent."
                )
                log_msg(json.dumps(data), label="Invitation Data:", color=None)
                qr.print_ascii(invert=True)
                log_msg("If you can't scan the QR code here is the url.")
                print("Invitation url:", invitation_url)
                print(
                    "================================================================="
                )

                return (
                    200,
                    json.dumps(
                        {
                            "result": "ok",
                            "connection_id": "1",
                            "state": self.connection_state,
                        }
                    ),
                )

            elif (
                operation == "accept-invitation"
                or operation == "accept-request"
                or operation == "remove"
                or operation == "start-introduction"
                or operation == "send-ping"
            ):
                self.connection_state = "requested"
                return (
                    200,
                    json.dumps(
                        {
                            "result": "ok",
                            "connection_id": "1",
                            "state": self.connection_state,
                        }
                    ),
                )

        elif command.topic == "issue-credential":
            if operation == "send-request":
                print(
                    "================================================================="
                )
                print("Please respond to the Credential Offer!")
                print(
                    "================================================================="
                )
                return (
                    200,
                    '{"result": "ok", "thread_id": "1", "state": "request-sent"}',
                )
            elif operation == "store":
                return (
                    200,
                    json.dumps(
                        {
                            "result": "ok",
                            "thread_id": "1",
                            "credential_id": record_id,
                            "state": "done",
                        }
                    ),
                )
            else:
                return (200, '{"result": "ok", "thread_id": "1", "state": "N/A"}')

        elif command.topic == "proof":
            if operation == "send-presentation":
                print(
                    "================================================================="
                )
                print("Please respond to the Proof Request!")
                print(
                    "================================================================="
                )
                return (
                    200,
                    '{"result": "ok", "thread_id": "1", "state": "presentation-sent"}',
                )
            else:
                return (200, '{"result": "ok", "thread_id": "1", "state": "N/A"}')

        return (501, "501: Not Implemented\n\n")

    async def make_agent_GET_request(
        self, command: BackchannelCommand
    ) -> Tuple[int, str]:
        print("make_agent_GET_request:", command)

        record_id = command.record_id

        if command.topic == "status":
            status = 200 if self.ACTIVE else 418
            status_msg = "Active" if self.ACTIVE else "Inactive"
            return (status, json.dumps({"status": status_msg}))

        elif command.topic == "connection":
            return (200, '{"result": "ok", "connection_id": "1", "state": "N/A"}')

        elif command.topic == "issue-credential":
            return (
                200,
                json.dumps(
                    {"result": "ok", "credential_id": record_id, "state": "N/A"}
                ),
            )

        elif command.topic == "credential":
            return (
                200,
                json.dumps(
                    {"result": "ok", "credential_id": record_id, "state": "N/A"}
                ),
            )

        elif command.topic == "proof":
            return (
                200,
                json.dumps({"result": "ok", "thread_id": record_id, "state": "N/A"}),
            )

        if command.topic == "version":
            return (200, '{"result": "ok"}')

        return (501, "501: Not Implemented\n\n")

    async def make_agent_DELETE_request(
        self, command: BackchannelCommand
    ) -> Tuple[int, str]:

        return (501, "501: Not Implemented\n\n")

    async def make_agent_GET_request_response(
        self, command: BackchannelCommand
    ) -> Tuple[int, str]:
        record_id = command.record_id

        if command.topic == "connection" and record_id:
            connection_msg = pop_resource(record_id, "connection-msg")
            i = 0
            while connection_msg is None and i < MAX_TIMEOUT:
                sleep(1)
                connection_msg = pop_resource(record_id, "connection-msg")
                i = i + 1

            resp_status = 200
            if connection_msg:
                resp_text = json.dumps(connection_msg)
            else:
                resp_text = "{}"

            return (resp_status, resp_text)

        return (501, "501: Not Implemented\n\n")


async def main(start_port: int, show_timing: bool = False, interactive: bool = True):

    genesis = None
    agent = None

    agent_ports = AgentPorts(
        http=start_port + 1,
        admin=start_port + 2,
        ws=start_port + 3,
    )

    try:
        print("Starting mobile backchannel ...")
        agent = MobileAgentBackchannel("mobile", agent_ports, genesis_data=genesis)

        # start backchannel (common across all types of agents)
        await agent.listen_backchannel(start_port)

        agent.activate()

        # now wait ...
        if interactive:
            async for option in prompt_loop("(X) Exit? [X] "):
                if option is None or option in "xX":
                    break
        else:
            print("Press Ctrl-C to exit ...")
            remaining_tasks = asyncio.Task.all_tasks()
            await asyncio.gather(*remaining_tasks)

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


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


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
    parser.add_argument(
        "-i",
        "--interactive",
        type=str2bool,
        default=True,
        metavar=("<interactive>"),
        help="Start agent interactively",
    )
    args = parser.parse_args()

    try:
        asyncio.get_event_loop().run_until_complete(
            main(start_port=args.port, interactive=args.interactive)
        )
    except KeyboardInterrupt:
        os._exit(1)
