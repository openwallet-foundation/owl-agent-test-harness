import asyncio
import functools
import json
import logging
import os
import random
import subprocess
import sys
from timeit import default_timer
from ctypes import cdll
from time import sleep

from aiohttp import (
    web,
    ClientSession,
    ClientRequest,
    ClientResponse,
    ClientError,
    ClientTimeout,
)

from python.agent_backchannel import AgentBackchannel, default_genesis_txns, RUN_MODE, START_TIMEOUT
from python.utils import require_indy, flatten, log_json, log_msg, log_timer, output_reader, prompt_loop, file_ext, create_uuid
from python.storage import store_resource, get_resource, delete_resource, pop_resource, get_resources

from vcx.api.connection import Connection
from vcx.api.credential_def import CredentialDef
from vcx.api.issuer_credential import IssuerCredential
from vcx.api.proof import Proof
from vcx.api.schema import Schema
from vcx.api.utils import vcx_agent_provision
from vcx.api.vcx_init import vcx_init_with_config
from vcx.state import State, ProofState


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


# 'agency_url': URL of the agency
# 'agency_did':  public DID of the agency
# 'agency_verkey': public verkey of the agency
# 'wallet_name': name for newly created encrypted wallet
# 'wallet_key': encryption key for encoding wallet
# 'payment_method': method that will be used for payments
provisionConfig = {
    'agency_url': 'http://$DOCKERHOST:$AGENCY_PORT',
    'agency_did': 'VsKV7grR1BUE29mG2Fm2kX',
    'agency_verkey': 'Hezce2UWMZ3wUhVkh2LfKSs8nDzWwzs2Win7EzNN3YaR',
    'wallet_name': 'faber_wallet',
    'wallet_key': '123',
    'payment_method': 'null',
    'enterprise_seed': '000000000000000000000000Trustee1',
    'protocol_type': '2.0',
    'communication_method': 'aries'
}


def state_text(connection_state):
    if connection_state == State.OfferSent:
        return "invitation"
    elif connection_state == State.RequestReceived:
        return "request"
    elif connection_state == State.Unfulfilled:
        return "response"
    elif connection_state == State.Accepted:
        return "active"
    return str(connection_state)


class VCXAgentBackchannel(AgentBackchannel):
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

    def rewrite_config(self, input_config, output_config, mappings):
        """Substitute our specific config parameters"""
        print("Writing config file:", output_config)
        with open(input_config,"r") as in_file:
            with open(output_config,"w") as out_file:
                config = in_file.read()
                for k, v in mappings.items():
                    config = config.replace(k, v)
                out_file.write(config)

    async def start_vcx(self):
        payment_plugin = cdll.LoadLibrary('libnullpay' + file_ext())
        payment_plugin.nullpay_init()

        print("Start vcx agency process")
        # http port is the main agency port
        # admin_port and admin_port+1 are used by the agency server
        # we need to rewrite these to the config file
        input_config = "vcx/vcx_agency/agency_config.json.template"
        self.output_config = "vcx/vcx_agency/agency_config.json"
        agency_host = os.getenv("DOCKERHOST") or "host.docker.internal"
        self.rewrite_config(
            input_config,
            self.output_config,
            {
                "$DOCKERHOST": agency_host,
                "$AGENCY_PORT": str(self.http_port),
                "$AGENCY_ADDRESS_1": str(self.admin_port),
                "$AGENCY_ADDRESS_2": str(self.admin_port+1),
            }
        )
        await self.start_vcx_agency()

        print("Provision an agent and wallet, get back configuration details")
        provisionConfig["agency_url"] = "http://localhost:" + str(self.admin_port)
        config = await vcx_agent_provision(json.dumps(provisionConfig))
        config = json.loads(config)
        # Set some additional configuration options specific to faber
        config['institution_name'] = 'Faber'
        config['institution_logo_url'] = 'http://robohash.org/234'
        config['genesis_path'] = 'genesis_txn.txt'
        with open(config['genesis_path'], "w") as f_genesis:
            f_genesis.write(self.genesis_data)

        print("Initialize libvcx with new configuration")
        await vcx_init_with_config(json.dumps(config))

        pass

    async def make_agent_POST_request(
        self, op, rec_id=None, data=None, text=False, params=None
    ) -> (int, str):
        if op["topic"] == "connection":
            operation = op["operation"]
            if operation == "create-invitation":
                connection_id = create_uuid()

                connection = await Connection.create(connection_id)
                await connection.connect('{"use_public_did": true}')
                invitation = await connection.invite_details(False)

                store_resource(connection_id, "connection", connection)
                connection_dict = await connection.serialize()

                resp_status = 200
                resp_text = json.dumps({"connection_id": connection_id, "invitation": invitation, "connection": connection_dict})

                return (resp_status, resp_text)

            elif operation == "receive-invitation":
                connection_id = create_uuid()

                connection = await Connection.create_with_details(connection_id, json.dumps(data))
                await connection.connect('{"use_public_did": true}')
                connection_state = await connection.update_state()
                store_resource(connection_id, "connection", connection)
                connection_dict = await connection.serialize()

                resp_status = 200
                resp_text = json.dumps({"connection_id": connection_id, "invitation": data, "connection": connection_dict})

                return (resp_status, resp_text)

            elif (operation == "accept-invitation" 
                or operation == "accept-request"
                or operation == "remove"
                or operation == "start-introduction"
                or operation == "send-ping"
            ):
                connection_id = rec_id
                connection = get_resource(rec_id, "connection")
                if connection:
                    # wait for a small period just in case ...
                    await asyncio.sleep(0.1)
                    # make sure we have latest & greatest connection state
                    await connection.update_state()
                    store_resource(connection_id, "connection", connection)
                    connection_dict = await connection.serialize()
                    connection_state = await connection.get_state()

                    resp_status = 200
                    resp_text = json.dumps({"connection_id": rec_id, "state": state_text(connection_state), "connection": connection_dict})
                    return (resp_status, resp_text)

        return (404, '404: Not Found\n\n'.encode('utf8'))

    async def make_agent_GET_request(
        self, op, rec_id=None, text=False, params=None
    ) -> (int, str):
        if op["topic"] == "status":
            status = 200 if self.ACTIVE else 418
            status_msg = "Active" if self.ACTIVE else "Inactive"
            return (status, json.dumps({"status": status_msg}))

        elif op["topic"] == "connection":
            if rec_id:
                log_msg("Getting connection for", rec_id)
                connection = get_resource(rec_id, "connection")

                if connection:
                    connection_dict = await connection.serialize()
                    connection_state = await connection.get_state()

                    resp_status = 200
                    resp_text = json.dumps({"connection_id": rec_id, "state": state_text(connection_state), "connection": connection_dict})
                    return (resp_status, resp_text)

            else:
                log_msg("Getting connections")
                connections = get_resources("connection")
                log_msg(connections)
                ret_connections = []
                for connection_id in connections:
                    connection = connections[connection_id]
                    connection_dict = await connection.serialize()
                    connection_state = await connection.get_state()
                    ret_connections.append({"connection_id": connection_id, "state": state_text(connection_state), "connection": connection_dict})

                resp_status = 200
                resp_text = json.dumps(ret_connections)
                log_msg(resp_status, resp_text)
                return (resp_status, resp_text)

        log_msg("Returning 404")

        return (404, '404: Not Found\n\n'.encode('utf8'))

    async def make_agent_GET_request_response(
        self, topic, rec_id=None, text=False, params=None
    ) -> (int, str):
        if topic == "connection" and rec_id:
            connection = get_resource(rec_id, "connection")
            connection_state = await connection.update_state()
            store_resource(rec_id, "connection", connection)

            resp_status = 200
            connection_dict = await connection.serialize()
            resp_text = json.dumps({"connection_id": rec_id, "connection": connection_dict})

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

    def get_agent_args(self):
        result = [self.output_config,]

        return result

    def get_process_args(self, bin_path: str = None):
        #TODO aca-py needs to be in the path so no need to give it a cmd_path
        cmd_path = "indy-dummy-agent"
        if bin_path is None:
            bin_path = DEFAULT_BIN_PATH
        if bin_path:
            cmd_path = os.path.join(bin_path, cmd_path)
        return list(flatten((cmd_path, self.get_agent_args())))

    async def start_vcx_agency(
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
            await asyncio.sleep(5.0)

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

async def main(start_port: int, show_timing: bool = False, interactive: bool = True):

    genesis = await default_genesis_txns()
    if not genesis:
        print("Error retrieving ledger genesis transactions")
        sys.exit(1)

    agent = None

    try:
        agent = VCXAgentBackchannel(
            "vcx", start_port+1, start_port+2, genesis_data=genesis
        )

        # start backchannel (common across all types of agents)
        await agent.listen_backchannel(start_port)

        # TODO start VCX agent sub-process 
        await agent.register_did()

        await agent.start_vcx()
        agent.activate()

        # now wait ...
        if interactive:
            async for option in prompt_loop(
                "(X) Exit? [X] "
            ):
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
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Runs a VCX demo agent.")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8050,
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

    require_indy()

    try:
        asyncio.get_event_loop().run_until_complete(main(args.port, interactive=args.interactive))
    except KeyboardInterrupt:
        os._exit(1)
