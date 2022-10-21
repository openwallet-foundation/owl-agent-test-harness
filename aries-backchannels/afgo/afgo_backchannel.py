import asyncio
import functools
import json
import logging
import os
import subprocess
from typing import Any, Dict, List, Mapping, Optional, Tuple
from typing_extensions import Literal
import uuid
import base64
import datetime
from timeit import default_timer
import base58

from aiohttp import (
    web,
    ClientSession,
    ClientRequest,
    ClientError,
    ClientTimeout,
)

from python.agent_backchannel import (
    AgentBackchannel,
    RUN_MODE,
    START_TIMEOUT,
    BackchannelCommand,
    AgentPorts,
)
from python.utils import flatten, log_msg, output_reader, prompt_loop, pad_base64
from python.storage import (
    get_resource,
    push_resource,
    pop_resource,
    pop_resource_latest,
    get_resource_latest,
)
from python.message_queue import (
    push_message_queue,
    pop_message_queue,
    push_message_stack,
    pop_message_stack,
)
from afgo.routes.mediation_routes import routes as mediation_routes

LOGGER = logging.getLogger(__name__)

MAX_TIMEOUT = 20

DEFAULT_BIN_PATH = "../venv/bin"
DEFAULT_PYTHON_PATH = ".."

if RUN_MODE == "docker":
    DEFAULT_BIN_PATH = "./bin"
    DEFAULT_PYTHON_PATH = "."
elif RUN_MODE == "pwd":
    DEFAULT_BIN_PATH = "./bin"
    DEFAULT_PYTHON_PATH = "."


class AfGoAgentBackchannel(AgentBackchannel):
    afgo_version = None
    current_webhook_topic = None
    did_data = None
    wehhook_state = None
    indx = 0

    # agent connection
    agent_invitation_id = None
    agent_connection_id = None

    myDID = None
    myKeyId = None

    def __init__(
        self,
        ident: str,
        agent_ports: AgentPorts,
        genesis_data: str = None,
        params: dict = {},
    ):
        super().__init__(ident, agent_ports, genesis_data, params)

        self.output_handler_futures = []
        self.agent_meta_params = {}

        # Afgo : RFC
        self.connectionResponderStateTranslationDict = {
            "invited": "invitation-received",
            "invitation": "invited",
            "requested": "request-received",
            "responded": "response-sent",
            "response": "responded",
            "invitation-sent": "invitation-sent",
            "completed": "completed",
        }

        # Afgo : RFC
        self.connectionRequesterStateTranslationDict = {
            "invited": "invitation-received",
            "invitation": "invited",
            "requested": "request-sent",
            "response": "responded",
            "completed": "completed",
        }

        # afgo : RFC
        self.issueCredentialStateTranslationDict = {
            "proposal_sent": "proposal-sent",
            "proposal_received": "proposal-received",
            "offer_sent": "offer-sent",
            "offer_received": "offer-received",
            "request_sent": "request-sent",
            "request_received": "request-received",
            "credential-issued": "credential-issued",
            "credential-received": "credential-received",
            "done": "done",
        }

        self.tempIssureCredentialStateTranslationDict = {
            "proposal-sent": "offer-received",
            "offer-sent": "request-received",
            "request-sent": "credential-received",
        }

        # afgo : RFC
        self.presentProofStateTranslationDict = {
            "request-sent": "request-sent",
            "request-received": "request-received",
            "proposal-sent": "proposal-sent",
            "proposal-received": "proposal-received",
            "presentation-sent": "presentation-sent",
            "presentation-received": "presentation-received",
            "done": "done",
            "abandoned": "abandoned",
        }

        # AATH API : AFGO Admin API
        self.issueCredentialOperationTranslationDict = {
            "prepare-json-ld": "prepare-json-ld",
            "send-proposal": "send-proposal",
            "send-offer": "send-offer",
            "send-request": "send-request",
        }

        # AATH API : AFGO Admin API
        self.issueCredentialWRecIDOperationTranslationDict = {
            "prepare-json-ld": "prepare-json-ld",
            "send-proposal": "send-proposal",
            "send-offer": "accept-proposal",
            "send-request": "accept-offer",
            "issue": "accept-request",
            "store": "accept-credential",
        }

        # Issue Cred  didcom type : AATH Expected State
        self.IssueCredentialTypeToStateTranslationDict = {
            "https://didcomm.org/issue-credential/2.0/offer-credential": "offer-received",
            "https://didcomm.org/issue-credential/2.0/request-credential": "request-received",
            "https://didcomm.org/issue-credential/2.0/issue-credential": "credential-received",
        }

        # Proof didcom type : AATH Expected State
        self.ProofTypeToStateTranslationDict = {
            "https://didcomm.org/present-proof/2.0/request-presentation": "request-received",
            "https://didcomm.org/present-proof/2.0/presentation": "presentation-received",
        }

        # credential format types to the format the tests expect
        self.CredentialFromatTranslationDict = {
            "hlindy/cred-filter@v2.0": "indy",
            "aries/ld-proof-vc@v1.0": "json-ld",
        }

        # AATH API : AFGO Admin API
        self.proofOperationTranslationDict = {
            "prepare-json-ld": "",
            "send-proposal": "send-propose-presentation",
            "accept-proposal": "accept-propose-presentation",
            "send-request": "send-request-presentation",
            "send-presentation": "accept-request-presentation",
            "verify-presentation": "accept-presentation",
        }

        self.map_test_ops_to_bachchannel = {
            "send-invitation-message": "create-invitation",
            "receive-invitation": "accept-invitation",
        }

        # AATH API : AFGO Admin API
        self.TopicTranslationDict = {
            "issue-credential": "/issuecredential/",
            "issue-credential-v2": "/issuecredential/",
            "issue-credential-v3": "/issuecredential/",
            "proof": "/presentproof/",
            "proof-v2": "/presentproof/",
            "proof-v3": "/presentproof/",
        }

        self.proofTypeKeyTypeTranslationDict = {
            "Ed25519Signature2018": "ED25519",
            "BbsBlsSignature2020": "BLS12381G2",
        }
        self.keyTypeVerificationMethodTypeTranslationDict = {
            "ED25519": "Ed25519VerificationKey2018",
            "BLS12381G2": "Bls12381G2Key2020",
        }

        # Generic AATH parameter to AFGO commandline parameter
        self.map_cmdline_params = {"mime-type": "media-type-profiles"}

    def get_agent_args(self):
        # FOR EXAMPLE:
        # ./bin/aries-agent-rest start \
        #    --inbound-host-external "http@http://192.168.65.3:8001/" \
        #    --agent-default-label ian-agent \
        #    --inbound-host "http@0.0.0.0:8002" \
        #    --outbound-transport http \
        #    --api-host "0.0.0.0:8010" \
        #    --database-type mem \
        #    --webhook-url "http://192.168.65.3:8020"

        result: List[Tuple[str, str]] = [
            ("--agent-default-label", self.label),
            ("--api-host", "0.0.0.0:" + str(self.agent_ports["admin"])),
            (
                "--database-type",
                "mem",
            ),
        ]
        if self.webhook_url:
            result.append(("--webhook-url", self.webhook_url))

        return result

    def get_host_args(
        self,
        inbound_transports: List[Literal["ws", "http"]],
        outbound_transports: List[Literal["ws", "http"]],
    ) -> List[str]:
        args: List[str] = []

        for transport in inbound_transports:
            port = self.agent_ports[transport]
            endpoint = self.get_agent_endpoint(transport)

            args += [
                "--inbound-host-external",
                f"{transport}@{endpoint}",
                "--inbound-host",
                f"{transport}@0.0.0.0:{port}",
            ]

        # If we don't have any inbound transports we can use return routing
        # to still be able to interact with other agents.
        if len(inbound_transports) == 0:
            args += ["--transport-return-route", "all"]

        for transport in outbound_transports:
            args += ["--outbound-transport", transport]

        return args

    async def listen_webhooks(self, webhook_port: int):
        self.webhook_port = webhook_port
        if RUN_MODE == "pwd":
            self.webhook_url = f"http://localhost:{str(webhook_port)}/webhooks"
        else:
            self.webhook_url = (
                f"http://{self.external_host}:{str(webhook_port)}/webhooks"
            )
        app = web.Application()
        app.add_routes([web.post("/webhooks", self._receive_webhook)])
        runner = web.AppRunner(app)
        await runner.setup()
        self.webhook_site = web.TCPSite(runner, "0.0.0.0", webhook_port)
        await self.webhook_site.start()
        print("Listening to web_hooks on port", webhook_port)

    async def _receive_webhook(self, request: ClientRequest):
        payload = await request.json()
        topic = payload["topic"]
        await self.handle_webhook(topic, payload)
        # TODO web hooks don't require a response???
        return web.Response(text="")

    async def handle_webhook(self, topic: str, payload):
        if topic != "webhook":  # would recurse
            handler = f"handle_{topic}"
            # adjust method names to change hyphens to underscores
            handler = handler.replace("-", "_")
            method = getattr(self, handler, None)

            # put a log message here
            log_msg("Passing webhook payload to handler " + handler)
            if method:
                await method(payload)
            else:
                log_msg(
                    f"Error: agent {self.ident} "
                    f"has no method {handler} "
                    f"to handle webhook on topic {topic}"
                )
        else:
            log_msg(
                "in webhook, topic is: " + topic + " payload is: " + json.dumps(payload)
            )

    async def handle_out_of_band_states(self, message: Mapping[str, Any]):
        if "id" in message:
            # connectionID may be best
            id_key = message["id"]
            push_resource(id_key, "out-of-band-states-msg", message)
        else:
            raise Exception(
                f"Unexpected id in out_of_band_states Webhook Message: {json.dumps(message)}"
            )
        log_msg(
            f"Processed a out-of-band-states Webhook message: {json.dumps(message)}"
        )

    async def handle_didexchange_states(self, message: Mapping[str, Any]):
        # oob didexcahgne states are usually invitations
        if "invitationID" in message["message"]["Properties"]:
            invitation_id = message["message"]["Properties"]["invitationID"]
            # push_resource(invitation_id, "didexchange-states-msg", message)
            await push_message_queue(
                "didexchange-states-msg" + "," + invitation_id, message
            )
            # backup: shared stack, for cases when the consumer doesn't know the current connection ID / invitation ID
            await push_message_stack("didexchange-states-msg", message)
        else:
            raise Exception(
                f"invitation_ID not found in didexchange_states Webhook Message: {json.dumps(message)}"
            )
        print("Processed a didexchange_states Webhook message: " + json.dumps(message))

    async def handle_didexchange_actions(self, message: Mapping[str, Any]):
        if "connectionID" in message["message"]["Properties"]:
            conection_id = message["message"]["Properties"]["connectionID"]
            push_resource(conection_id, "didexchange-actions-msg", message)
        else:
            raise Exception(
                f"connectionID not found in didexchange_actions Webhook Message: {json.dumps(message)}"
            )
        log_msg(
            "Processed a didexchange_actions Webhook message: " + json.dumps(message)
        )

    async def handle_issue_credential_states(self, message: Mapping[str, Any]):
        if "piid" in message["message"]["Properties"]:
            thread_id = message["message"]["Properties"]["piid"]
            push_resource(thread_id, "issue-credential-states-msg", message)
        else:
            raise Exception(
                f"piid not found in issue_credential_states Webhook Message: {json.dumps(message)}"
            )
        log_msg(
            f"Processed issue_credential_states Webhook message: {json.dumps(message)}"
        )
        if "revocation_id" in message:  # also push as a revocation message
            push_resource(thread_id, "revocation-registry-msg", message)
            log_msg("Issue Credential Webhook message contains revocation info")

    async def handle_issue_credential_actions(self, message: Mapping[str, Any]):
        if "piid" in message["message"]["Properties"]:
            thread_id = message["message"]["Properties"]["piid"]
            push_resource(thread_id, "issue-credential-actions-msg", message)
        else:
            raise Exception(
                f"piid not found in issue_credential_actions Webhook Message: {json.dumps(message)}"
            )
        log_msg(
            f"Processed issue_credential_actions Webhook message: {json.dumps(message)}"
        )

    async def handle_present_proof_states(self, message: Mapping[str, Any]):
        if "piid" in message["message"]["Properties"]:
            thread_id = message["message"]["Properties"]["piid"]
            push_resource(thread_id, "present-proof-states-msg", message)

            await push_message_stack("present-proof-states-msg" + "," + thread_id, message)
        else:
            raise Exception(
                f"piid not found in present_proof_states Webhook Message: {json.dumps(message)}"
            )
        log_msg(
            f"Processed present_proof_states Webhook message: {json.dumps(message)}"
        )

    async def handle_present_proof_actions(self, message: Mapping[str, Any]):
        if "piid" in message["message"]["Properties"]:
            thread_id = message["message"]["Properties"]["piid"]
            push_resource(thread_id, "present-proof-actions-msg", message)
        else:
            raise Exception(
                f"piid not found in present_proof_actions Webhook Message: {json.dumps(message)}"
            )
        log_msg(
            f"Processed present_proof_actions Webhook message: {json.dumps(message)}"
        )

    async def handle_present_proof(self, message: Mapping[str, Any]):
        thread_id = message["thread_id"]

        # if has state
        if "StateID" in message["message"]:
            self.webhook_state = message["message"]["StateID"]

        push_resource(thread_id, "presentation-msg", message)
        log_msg("Received a Present Proof Webhook message: " + json.dumps(message))

    async def handle_revocation_registry(self, message: Mapping[str, Any]):
        # No thread id in the webhook for revocation registry messages
        cred_def_id = message["cred_def_id"]
        push_resource(cred_def_id, "revocation-registry-msg", message)
        log_msg("Received Revocation Registry Webhook message: " + json.dumps(message))

    async def handle_problem_report(self, message: Mapping[str, Any]):
        thread_id = message["thread_id"]
        push_resource(thread_id, "problem-report-msg", message)
        log_msg("Received Problem Report Webhook message: " + json.dumps(message))

    async def swap_thread_id_for_exchange_id(
        self, thread_id: str, data_type: str, id_txt: str
    ):
        timeout = 0
        webcall_returned = None
        while webcall_returned is None or timeout == 20:
            msg = get_resource(thread_id, data_type)
            try:
                ex_id = msg[0][id_txt]
                webcall_returned = True
            except TypeError:
                await asyncio.sleep(1)
                timeout += 1
        if timeout == 20:
            raise TimeoutError(
                "Timeout waiting for web callback to retrieve the thread id based on the exchange id"
            )
        return ex_id

    async def make_admin_request(
        self,
        method: str,
        path: str,
        data: Optional[Any] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[int, str]:
        params = {k: v for (k, v) in (params or {}).items() if v is not None}
        async with self.client_session.request(
            method, self.admin_url + path, json=data, params=params
        ) as resp:
            resp_status = resp.status
            resp_text = await resp.text()
            return (resp_status, resp_text)

    async def admin_GET(
        self, path: str, params: Optional[Mapping[str, Any]] = None
    ) -> Tuple[int, str]:
        try:
            return await self.make_admin_request("GET", path, None, params)
        except ClientError as e:
            self.log(f"Error during GET {path}: {str(e)}")
            raise

    async def admin_DELETE(
        self, path: str, params: Optional[Mapping[str, Any]] = None
    ) -> Tuple[int, str]:
        try:
            return await self.make_admin_request("DELETE", path, None, params)
        except ClientError as e:
            self.log(f"Error during DELETE {path}: {str(e)}")
            raise

    async def admin_POST(
        self,
        path: str,
        data: Optional[Any] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[int, str]:
        try:
            return await self.make_admin_request("POST", path, data, params)
        except ClientError as e:
            self.log(f"Error during POST {path}: {str(e)}")
            raise

    async def make_agent_POST_request(
        self, command: BackchannelCommand
    ) -> Tuple[int, str]:

        if command.topic == "connection":
            # TODO: legacy code from acapy backchannel
            operation = command.operation
            if operation == "create-invitation":
                agent_operation = "/connections/" + operation

                (resp_status, resp_text) = await self.admin_POST(agent_operation)

                # extract invitation from the agent's response
                invitation_resp = json.loads(resp_text)
                resp_text = json.dumps(invitation_resp)

                if resp_status == 200:
                    resp_text = self.agent_state_translation(
                        command.topic, operation, resp_text
                    )
                return (resp_status, resp_text)

            elif operation == "receive-invitation":
                agent_operation = "/connections/" + operation

                (resp_status, resp_text) = await self.admin_POST(
                    agent_operation, data=command.data
                )
                if resp_status == 200:
                    resp_text = self.agent_state_translation(
                        command.topic, None, resp_text
                    )
                return (resp_status, resp_text)

            elif (
                operation == "accept-invitation"
                or operation == "accept-request"
                or operation == "remove"
                or operation == "start-introduction"
                or operation == "send-ping"
            ):
                connection_id = command.record_id
                agent_operation = f"/connections/{connection_id}/{operation}"
                log_msg("POST Request: ", agent_operation, command.data)

                (resp_status, resp_text) = await self.admin_POST(
                    agent_operation, command.data
                )

                log_msg(resp_status, resp_text)
                if resp_status == 200:
                    resp_text = self.agent_state_translation(
                        command.topic, None, resp_text
                    )
                return (resp_status, resp_text)

        elif command.topic == "schema":
            log_msg(
                "afgo does not support the creation of schema. This call is returning what the test expects without a call to afgo"
            )

            resp_json = {"schema_id": "not supported by afgo"}
            return (200, json.dumps(resp_json))

        elif command.topic == "credential-definition":
            log_msg(
                "afgo does not support the creation of credential defintion. This call is returning what the test expects without a call to afgo"
            )

            resp_json = {"credential_definition_id": ""}
            return (200, json.dumps(resp_json))

        elif (
            command.topic == "issue-credential"
            or command.topic == "issue-credential-v2"
            or command.topic == "issue-credential-v3"
        ):
            (resp_status, resp_text) = await self.handle_issue_credential_POST(command)
            return (resp_status, resp_text)

        elif command.topic == "revocation":
            log_msg("afgo does not support indy revocation.")

            resp_json = {"indy_revocation": "not supported by afgo"}
            return (200, json.dumps(resp_json))

        elif command.topic == "proof" or command.topic == "proof-v2":
            (resp_status, resp_text) = await self.handle_present_proof_POST(command)
            return (resp_status, resp_text)

        elif command.topic == "proof-v3":
            (resp_status, resp_text) = await self.handle_present_proof_v3_POST(command)
            return (resp_status, resp_text)

        # Handle out of band POST operations
        elif command.topic == "out-of-band":
            (resp_status, resp_text) = await self.handle_out_of_band_POST(command)
            return (resp_status, resp_text)

        # Handle did exchange POST operations
        elif command.topic == "did-exchange":
            (resp_status, resp_text) = await self.handle_did_exchange_POST(command)
            return (resp_status, resp_text)

        elif command.topic == "agent":
            (resp_status, resp_text) = await self.handle_agent_POST(command)
            return (resp_status, resp_text)

        elif command.topic == "oob-v2":
            (resp_status, resp_text) = await self.handle_oob_v2_POST(command)
            return (resp_status, resp_text)

        return (501, "501: Not Implemented\n\n")

    async def handle_agent_POST(self, command: BackchannelCommand):
        data = command.data

        if command.operation != "start":
            return (404, "Unsupported operation")

        input_params: Dict[str, Any] = data["parameters"]
        print(f"(re)start agent with params: {input_params}")

        self.agent_meta_params = {}

        # Get agent host args. If inbound / outbound transports is not provided we use http by default
        # If an empty array is provided it means we don't want to use any transport
        # Useful for testing agents without endpoint
        inbound: List[str] = input_params.get("inbound_transports", ["http"])
        outbound: List[str] = input_params.get("outbound_transports", ["http"])

        args = self.get_host_args(
            inbound_transports=inbound,
            outbound_transports=outbound,
        )

        for key, value in input_params.items():
            arg = key
            if arg in self.map_cmdline_params:
                arg = self.map_cmdline_params[arg]
            else:
                # parameters that aren't mapped to the agent will stay in the backchannel
                self.agent_meta_params[key] = value
                continue

            arg = "--" + arg

            args.append(arg)

            if value:
                # if v is a list, make it a csv string
                if isinstance(value, list):
                    value = ",".join(value)

                args.append(value)

        await self.kill_agent()
        await self.start_process_with_extra_args(args=args)

        return (200, "{}")

    async def handle_oob_v2_POST(self, command: BackchannelCommand):
        operation = command.operation
        data = command.data

        if operation == "create-invitation":
            (
                orb_did_status,
                orb_did_text,
                priv_key_kids,
            ) = await self.get_orb_did()
            if orb_did_status != 200:
                err_msg = f"Couldn't retrieve my public did: status={orb_did_status} body={orb_did_text}"
                print(err_msg)

                return (500, err_msg)

            my_pub_did = json.loads(orb_did_text)["did"]

            afgo_endpoint = "/outofband/2.0/create-invitation"
            create_req = {
                "from": my_pub_did
            }

            if data and "goal-code" in data:
                create_req["body"] = {
                    "goal-code": data["goal-code"]
                }

            (resp_status, resp_text) = await self.admin_POST(afgo_endpoint, create_req)

            return (resp_status, resp_text)

        if operation == "accept-invitation":
            data["my_label"] = "dummy-label"

            afgo_endpoint = "/outofband/2.0/accept-invitation"

            (resp_status, resp_text) = await self.admin_POST(afgo_endpoint, data)
            # afgo's reponse object looks like {"connection_id":"<connection ID>"}
            return (resp_status, resp_text)

        return (501, f"didcomm v2 operation '{operation}' not implemented")

    async def handle_oob_v2_GET(self, command: BackchannelCommand):
        operation = command.operation

        if operation == "invitation-connection":
            connection_id = ""
            invitation_id = command.record_id

            afgo_endpoint = f"/connections"

            (resp_status, resp_text) = await self.admin_GET(afgo_endpoint)
            if resp_status != 200:
                return (resp_status, f"failed to query afgo connections, response: {resp_text}")

            resp_json = json.loads(resp_text)
            if "results" not in resp_json:
                return (500, f"failed to query afgo connections, missing connection list from {resp_text}")

            for connection in resp_json["results"]:
                log_msg(f"Check connection: {connection}")
                if connection["InvitationID"] == invitation_id:
                    connection_id = connection["ConnectionID"]
                    break

            response = {
                "connection_id": connection_id
            }

            return (200, json.dumps(response))

        return (501, f"didcomm v2 operation '{operation}' not implemented")

    async def handle_out_of_band_POST(self, command: BackchannelCommand):
        operation = command.operation
        data = command.data
        agent_operation = "outofband"

        if operation == "send-invitation-message":
            # This label is needed for the accept invitation.
            new_data = {"label": f"Invitation created by {self.admin_url}"}
            if "accept" in data:
                new_data["accept"] = data["accept"]
            elif "oob-accept" in self.agent_meta_params:
                new_data["accept"] = self.agent_meta_params["oob-accept"]

            # If mediator_connection_id is included we should use that as the mediator for this connection
            if (
                "mediator_connection_id" in data
                and data["mediator_connection_id"] != None
            ):
                new_data["router_connection_id"] = data["mediator_connection_id"]

        elif operation == "receive-invitation":
            # Accept invitation requires my_label be part of the data.
            # That is wy the create invitation above adds a label to have some consistency.
            new_data = {"invitation": data}
            new_data["my_label"] = data["label"]

            # If mediator_connection_id is included we should use that as the mediator for this connection
            if (
                "mediator_connection_id" in data
                and data["mediator_connection_id"] != None
            ):
                new_data["router_connections"] = data["mediator_connection_id"]

        data = new_data

        agent_operation = (
            f"/{agent_operation}/{self.map_test_ops_to_bachchannel[operation]}"
        )

        print(f"admin_POST to {agent_operation} with data {data}")

        (resp_status, resp_text) = await self.admin_POST(agent_operation, data)

        if resp_status == 200:
            # call get connection to get the status based on the invitation id.
            resp_text = await self.amend_response_with_state("connection", resp_text)
            resp_text = self.agent_state_translation(
                command.topic, operation, resp_text
            )
        return (resp_status, resp_text)

    async def amend_response_with_state(self, topic: str, resp_text: str):
        resp_json = json.loads(resp_text)
        if "invitation" in resp_json:
            params = {"invitation_id": resp_json["invitation"]["@id"]}
            (resp_status, get_resp_text) = await self.make_agent_GET_request(
                BackchannelCommand(
                    topic=topic, method="GET", operation=None, record_id=None, data=None
                ),
                params=params,
            )
        elif "connection_id" in resp_json:
            connection_id = resp_json["connection_id"]
            (resp_status, get_resp_text) = await self.admin_GET(
                f"/connections/{connection_id}"
            )
        get_resp_json = json.loads(get_resp_text)
        # if resp_status == 200 and len(get_resp_json) != 0:
        if resp_status == 200:
            if len(get_resp_json) != 0:
                if "results" in resp_json:
                    resp_json["state"] = get_resp_json["results"]["State"]
                else:
                    resp_json["state"] = get_resp_json["result"]["State"]
            else:
                # If the message is empty with 200, it probably means that an invitation was created
                # but no conection record exists yet. Set the state to invitation-sent
                resp_json["state"] = "invitation-sent"
        else:
            log_msg(
                f"Could not retrieve state information - {resp_status}: {get_resp_text}"
            )
        return json.dumps(resp_json)

    async def get_DIDs_for_participants(self, connection_id: str):
        operation = f"/connections/{connection_id}"
        (resp_status, resp_text) = await self.admin_GET(operation)
        if resp_status == 200:
            resp_json = json.loads(resp_text)
            if "TheirDID" in resp_text:
                their_did = resp_json["result"]["TheirDID"]
            else:
                raise Exception(
                    f"TheirDID not returned with connection record: {resp_text}"
                )
            if "MyDID" in resp_text:
                my_did = resp_json["result"]["MyDID"]
            else:
                raise Exception(
                    f"MyDID not returned with connection record: {resp_text}"
                )
            return (their_did, my_did)
        else:
            raise Exception(
                f"Problem retreiving Connection record with Connection ID {connection_id}: {resp_status} - {resp_text} "
            )

    async def find_connection_by_invitation_id(self, invitation_id: str):
        if invitation_id != None:
            operation = "/connections"
            (resp_status, resp_text) = await self.admin_GET(operation)

            if resp_status == 200:
                resp_json = json.loads(resp_text)
                if "results" in resp_json:
                    for connection in resp_json["results"]:
                        if connection["InvitationID"] == invitation_id:
                            self.agent_connection_id = connection["ConnectionID"]

    async def handle_did_exchange_POST(self, command: BackchannelCommand):
        operation = command.operation
        record_id = command.record_id
        data = command.data
        agent_operation = "/connections/"  # did-exchange

        if operation == "send-message":
            agent_operation = f"/connections/{record_id}/accept-request"

        elif operation == "send-request":
            # Check the connection object for latest state
            resp_text = {"connection_id": record_id}
            await asyncio.sleep(3)
            resp_text = await self.amend_response_with_state(
                "connections", json.dumps(resp_text)
            )
            resp_status = 200
            # We know this is the requester because we are in send-request, so swap for expected requester state
            resp_text = self.agent_state_translation(
                command.topic, operation, resp_text
            )
            return (resp_status, resp_text)

        elif operation == "send-response":
            agent_operation = f"/connections/{record_id}/accept-request"
            params = {}

            # Mediator connection id must also be set for the accept-request message
            if (
                data
                and "mediator_connection_id" in data
                and data["mediator_connection_id"] != None
            ):
                params["router_connections"] = data["mediator_connection_id"]

            (resp_status, resp_text) = await self.admin_POST(
                agent_operation, data, params
            )
            if resp_status == 200:
                # Response doesn't have a state, get it from the connection record.
                resp_text = await self.amend_response_with_state(
                    "connections", resp_text
                )
                # Translate the given state to the expected RFC state.
                resp_text = self.agent_state_translation(
                    command.topic, operation, resp_text
                )
            elif resp_status == 500 and "code" in resp_text:
                resp_json = json.loads(resp_text)
                if resp_json["code"] == 2005:
                    resp_status = 400
            return (resp_status, resp_text)

        elif operation == "create-request-resolvable-did":
            their_public_did = data["their_public_did"]
            if not their_public_did.startswith("did:"):
                their_public_did = "did:sov:" + their_public_did
            # create and accept implicit invitation
            agent_operation = (
                f"/connections/create-implicit-invitation?their_did={their_public_did}"
            )

        elif operation == "receive-request-resolvable-did":
            # Note: we don't provide any rec_id in the receive-request-resolvable-did case.
            # this is because the agent with the public DID doesn't have a connection ID until it's received the front-channel
            # OOB message from the invitee.
            (resp_status, resp_text) = await self.request_response_did_exchange()
            return (resp_status, resp_text)

        (resp_status, resp_text) = await self.admin_POST(agent_operation, data)

        return (resp_status, resp_text)

    async def handle_issue_credential_POST(
        self, command: BackchannelCommand
    ) -> Tuple[int, str]:
        topic = command.topic
        operation = command.operation
        record_id = command.record_id
        data = command.data

        def make_agent_operation(record_id: str):
            return (
                self.TopicTranslationDict[topic]
                + record_id
                + "/"
                + self.issueCredentialWRecIDOperationTranslationDict[operation]
            )

        if record_id is None:
            agent_operation = f"{self.TopicTranslationDict[topic]}{self.issueCredentialOperationTranslationDict[operation]}"
        else:
            agent_operation = make_agent_operation(record_id)

        if data is not None:
            log_msg(
                f"Data passed to backchannel by test for operation: {agent_operation}",
                data,
            )

        await self.load_jsonld_contexts()

        isWACI = False

        if operation == "send-proposal" and "pthid" in data:
            isWACI = True
        elif operation == "send-offer":
            if isinstance(data, list) and "credential_manifest" in data[0]["data"]["json"]:
                isWACI = True
        elif operation == "send-request":
            if isinstance(data, list) and "credential_application" in data[0]["data"]["json"]:
                isWACI = True
        elif operation == "issue":
            if isinstance(data, list) and "credential_fulfillment" in data[0]["data"]["json"]:
                isWACI = True

        if operation == "prepare-json-ld":
            did_method = data["did_method"]
            if did_method == "orb":
                (orb_did_status, orb_did_text, priv_key_kids) = await self.get_orb_did()

                self.myKeyId = None
                return (orb_did_status, orb_did_text)
            elif did_method == "key":
                # create key set
                key_type = self.proofTypeKeyTypeTranslationDict[data["proof_type"]]
                (resp_status, resp_text) = await self.admin_POST(
                    "/kms/keyset", {"KeyType": key_type}
                )

                if resp_status != 200:
                    return (resp_status, resp_text)

                resp_json = json.loads(resp_text)

                public_key_base64 = resp_json["publicKey"]
                self.myKeyId = resp_json["keyID"]
                print("The public key is: ", public_key_base64)

                verification_method_type = (
                    self.keyTypeVerificationMethodTypeTranslationDict[key_type]
                )
                public_key_base58 = base58.b58encode(
                    base64.urlsafe_b64decode(pad_base64(public_key_base64))
                ).decode("ascii")
                print("The public key is: ", public_key_base58)

                did_document = {
                    "method": "key",
                    "did": {
                        "@context": [
                            "https://www.w3.org/ns/did/v1",
                        ],
                        "id": "",
                        "verificationMethod": [
                            {
                                "id": "",
                                "type": verification_method_type,
                                "controller": "",
                                "publicKeyBase58": public_key_base58,
                            }
                        ],
                    },
                    "opts": {"store": True},
                }

                (resp_status, resp_text) = await self.admin_POST(
                    "/vdr/did/create", did_document
                )

                if resp_status != 200:
                    return (resp_status, resp_text)

                resp_json = json.loads(resp_text)

                return (200, json.dumps({"did": resp_json["did"]["id"]}))
            else:
                return (500, f"Unsupported did method: {did_method}")

        if operation == "send-proposal" or operation == "send-offer":
            if operation == "send-proposal" and isWACI:
                # Get connection by connection id contained in the data received
                # Get the DID keys from the connection record
                (their_did, my_did) = await self.get_DIDs_for_participants(data["connectionID"])
                self.myDID = my_did

                data = {"pthid": data["pthid"],
                    "my_did": my_did,
                        "their_did": their_did,
                        "propose_credential": {}}

            elif operation == "send-offer" and isWACI:
                # The data passed in to the handler here contains just the
                # Credential Manifest and Credential Fulfillment preview attachments.
                # Below we arrange them as needed to be accepted by the AFGo agent's accept-proposal endpoint.

                (wh_status, wh_text) = await self.request_response_issue_credential(
                    rec_id=record_id, message_name="issue-credential-actions-msg"
                )
                issue_credential_actions_msg = json.loads(wh_text)

                record_id = issue_credential_actions_msg["message"]["Properties"]["piid"]

                agent_operation = make_agent_operation(record_id)

                data = {"offer_credential": {
                    "@type": "https://didcomm.org/issue-credential/3.0/offer-credential",
                    "attachments": data
                }}

            else:
                if data is None:
                    # get the credential_proposal from the webhook
                    if record_id is None:
                        raise Exception(
                            f"Cannot have both data and rec_id empty for issuecredential/{operation}"
                        )

                    (wh_status, wh_text) = await self.request_response_issue_credential(
                        rec_id=record_id, message_name="issue-credential-actions-msg"
                    )
                    issue_credential_actions_msg = json.loads(wh_text)
                    # Format the proposal for afgo offer

                    data = {}

                    cred_prev = {}

                    if (
                            "credential_proposal"
                            in issue_credential_actions_msg["message"]["Message"]
                    ):
                        cred_prev = issue_credential_actions_msg["message"]["Message"][
                            "credential_proposal"
                        ]
                    elif (
                            "credential_preview"
                            in issue_credential_actions_msg["message"]["Message"]
                    ):
                        cred_prev = issue_credential_actions_msg["message"]["Message"][
                            "credential_preview"
                        ]

                    if operation == "send-proposal" and not isWACI:
                        data["credential_proposal"] = cred_prev
                    elif operation == "send-offer" and not isWACI:
                        data["credential_preview"] = cred_prev

                    if (
                            "filters~attach"
                            in issue_credential_actions_msg["message"]["Message"]
                    ):
                        filters_attach = issue_credential_actions_msg["message"]["Message"][
                            "filters~attach"
                        ]
                        # TODO support more than one filter
                        if len(filters_attach) > 0:
                            filter_attmt = filters_attach[0]["data"]
                            if "json" in filter_attmt:
                                data["filter"] = filter_attmt["json"]
                            elif "base64" in filter_attmt:
                                filter_dec = base64.b64decode(filter_attmt["base64"])
                                filter_json = json.loads(filter_dec)
                                data["filter"] = filter_json

                    # Save Issuer DID off for ease of later use
                    self.myDID = issue_credential_actions_msg["message"]["Properties"][
                        "myDID"
                    ]
                    their_did = issue_credential_actions_msg["message"]["Properties"][
                        "theirDID"
                    ]

                    record_id = issue_credential_actions_msg["message"]["Properties"][
                        "piid"
                    ]
                else:
                    data_text = json.dumps(data)

                    # Get connection by connection id contained in the data received
                    # Get the DID keys from the connection record
                    (their_did, my_did) = await self.get_DIDs_for_participants(
                        data["connection_id"]
                    )
                    self.myDID = my_did

                    # remove schema/indy related items from data
                    if "schema_id" in data:
                        data.pop("schema_id")
                    if "schema_issuer_did" in data:
                        data.pop("schema_issuer_did")
                    if "issuer_did" in data:
                        data.pop("issuer_did")
                    if "schema_name" in data:
                        data.pop("schema_name")
                    if "cred_def_id" in data:
                        data.pop("cred_def_id")
                    if "schema_version" in data:
                        data.pop("schema_version")
                    if "connection_id" in data:
                        data.pop("connection_id")

                # add their did and my did to the data
                data["my_did"] = self.myDID
                data["their_did"] = their_did

            # Properly construct the credential proposal for afgo
            if operation == "send-proposal" and not isWACI:
                if "credential_proposal" in data:
                    data["propose_credential"] = {
                        "credential_proposal": data["credential_proposal"]
                    }
                    data.pop("credential_proposal")
                elif "credential_preview" in data:
                    data["propose_credential"] = {
                        "credential_proposal": data["credential_preview"]
                    }
                    data.pop("credential_preview")
                else:
                    raise Exception(
                        f"Message data passed for issuecredential/{command.operation} doesn't contain a credential_proposal: {data}"
                    )

                if "filter" in data:
                    # TODO support more than one filter
                    json_filter = data["filter"]
                    if "json-ld" in json_filter:
                        json_filter = json_filter["json-ld"]
                    elif "indy" in json_filter:
                        json_filter = json_filter["indy"]

                    # add an id for the filter
                    filter_id = str(uuid.uuid1())
                    # add mime_type (json)
                    mime_type = "application/json"
                    # add the filters~attach to the data
                    data["propose_credential"]["filters~attach"] = [
                        {
                            "@id": filter_id,
                            "mime_type": mime_type,
                            "data": {"json": json_filter},
                        }
                    ]
                    # add formats to the data with attach_id and format
                    if "indy" in data["filter"]:
                        filter_format = "hlindy/cred-filter@v2.0"
                    else:
                        filter_format = "aries/ld-proof-vc@v1.0"

                    data["propose_credential"]["formats"] = [
                        {"attach_id": filter_id, "format": filter_format}
                    ]

                    data.pop("filter")

            elif operation == "send-offer" and not isWACI:
                if "credential_preview" in data:
                    data["offer_credential"] = {
                        "credential_preview": data["credential_preview"]
                    }
                    data.pop("credential_preview")
                else:
                    raise Exception(
                        f"Message data passed for issuecredential/{command.operation} doesn't contain a credential_preview: {data}"
                    )

                if "filter" in data:
                    # TODO support more than one filter
                    # encode the json to base64
                    json_filter = data["filter"]
                    # json_filter_b64 = base64.b64encode(json_filter.encode('utf-8'))
                    # add an id for the filter
                    filter_id = str(uuid.uuid1())
                    # add mime_type (json)
                    mime_type = "application/json"
                    # add the filters~attach to the data
                    data["offer_credential"]["offers~attach"] = [
                        {
                            "@id": filter_id,
                            "mime_type": mime_type,
                            "data": {"json": json_filter},
                        }
                    ]
                    # add formats to the data with attach_id and format
                    if "indy" in data["filter"]:
                        filter_format = "hlindy/cred-filter@v2.0"
                    else:
                        filter_format = "aries/ld-proof-vc@v1.0"

                    data["offer_credential"]["formats"] = [
                        {"attach_id": filter_id, "format": filter_format}
                    ]

                    data.pop("filter")

            if record_id is not None:
                # in some cases we overwrite record_id with the correct piid
                agent_operation = make_agent_operation(record_id)

            log_msg(
                f"Data translated by backchannel to send to agent for operation: {agent_operation}",
                data,
            )

            (resp_status, resp_text) = await self.admin_POST(agent_operation, data)
            log_msg(resp_status, resp_text)
            resp_json = json.loads(resp_text)

            if resp_status == 200:
                # Get the state form the webhook callback.
                if record_id == None:
                    if "piid" in resp_json:
                        record_id = resp_json["piid"]
                    else:
                        raise Exception(
                            f"No piid found to retrieve State from webhook message: {resp_text}"
                        )
                (wh_status, wh_text) = await self.request_response_issue_credential(
                    record_id
                )
                issue_credential_states_msg = json.loads(wh_text)
                if "StateID" in issue_credential_states_msg["message"]:
                    resp_json["state"] = issue_credential_states_msg["message"][
                        "StateID"
                    ]
                else:
                    raise Exception(
                        f"Could not retieve State from webhook message: {issue_credential_states_msg}"
                    )

                if operation == "send-proposal":
                    resp_json["thread_id"] = resp_json["piid"]

                resp_text = json.dumps(resp_json)

            return (resp_status, resp_text)

        elif operation == "send-request" and isWACI:
            log_msg(
                f"Data translated by backchannel to send to agent for operation: {agent_operation}",
                data,
            )

            # The data passed in to the handler here contains just the
            # Credential Application attachment.
            # Below we arrange it as needed to be accepted by the AFGo agent's accept-offer endpoint.

            data = {
                "request_credential": {
                    "ID": "ae639a44-1c63-4d11-ba05-39a1f97993aa",
                    "Type": "https://didcomm.org/issue-credential/3.0/request-credential",
                    "Comment": "",
                    "GoalCode": "",
                    "Attachments": data
                }
            }

            (wh_status, wh_text) = await self.request_response_issue_credential(
                rec_id=record_id, message_name="issue-credential-actions-msg"
            )
            issue_credential_actions_msg = json.loads(wh_text)

            record_id = issue_credential_actions_msg["message"]["Properties"]["piid"]

            agent_operation = make_agent_operation(record_id)

            (resp_status, resp_text) = await self.admin_POST(agent_operation, data)

            log_msg(resp_status, resp_text)
            resp_json = json.loads(resp_text)

            if resp_status == 200:
                # Get the state form the webhook callback.
                if record_id == None:
                    if "piid" in resp_json:
                        record_id = resp_json["piid"]
                    else:
                        raise Exception(
                            f"No piid found to retrieve State from webhook message: {resp_text}"
                        )

                (wh_status, wh_text) = await self.request_response_issue_credential(
                    record_id
                )
                issue_credential_states_msg = json.loads(wh_text)
                if "StateID" in issue_credential_states_msg["message"]:
                    resp_json["state"] = issue_credential_states_msg["message"][
                        "StateID"
                    ]
                else:
                    raise Exception(
                        f"Could not retieve State from webhook message: {issue_credential_states_msg}"
                    )

                resp_json["thread_id"] = record_id

                resp_text = json.dumps(resp_json)

            return resp_status, resp_text

        elif operation == "send-request":
            (wh_status, wh_text) = await self.request_response_issue_credential(
                rec_id=record_id, message_name="issue-credential-actions-msg"
            )
            issue_credential_actions_msg = json.loads(wh_text)

            record_id = issue_credential_actions_msg["message"]["Properties"]["piid"]

            agent_operation = make_agent_operation(record_id)

            log_msg(
                f"Data translated by backchannel to send to agent for operation: {agent_operation}",
                data,
            )

            (resp_status, resp_text) = await self.admin_POST(agent_operation, data)
            log_msg(resp_status, resp_text)
            resp_json = json.loads(resp_text)

            if resp_status == 200:
                # Get the state form the webhook callback.
                if record_id == None:
                    if "piid" in resp_json:
                        record_id = resp_json["piid"]
                    else:
                        raise Exception(
                            f"No piid found to retrieve State from webhook message: {resp_text}"
                        )
                (wh_status, wh_text) = await self.request_response_issue_credential(
                    record_id
                )
                issue_credential_states_msg = json.loads(wh_text)
                if "StateID" in issue_credential_states_msg["message"]:
                    resp_json["state"] = issue_credential_states_msg["message"][
                        "StateID"
                    ]
                else:
                    raise Exception(
                        f"Could not retieve State from webhook message: {issue_credential_states_msg}"
                    )

                resp_json["thread_id"] = record_id

                resp_text = json.dumps(resp_json)

            return (resp_status, resp_text)

        elif operation == "store":
            (wh_status, wh_text) = await self.request_response_issue_credential(
                rec_id=record_id, message_name="issue-credential-actions-msg"
            )
            issue_credential_actions_msg = json.loads(wh_text)

            record_id = issue_credential_actions_msg["message"]["Properties"]["piid"]

            agent_operation = make_agent_operation(record_id)

            data = {"names": [record_id]}

            log_msg(
                f"Data translated by backchannel to send to agent for operation: {agent_operation}",
                data,
            )

            (resp_status, resp_text) = await self.admin_POST(agent_operation, data)
            log_msg(resp_status, resp_text)

            if resp_status == 200:
                resp_json = json.loads(resp_text)
                # Get the state form the webhook callback.
                if record_id == None:
                    if "piid" in resp_json:
                        record_id = resp_json["piid"]
                    else:
                        raise Exception(
                            f"No piid found to retrieve State from webhook message: {resp_text}"
                        )
                (wh_status, wh_text) = await self.request_response_issue_credential(
                    record_id
                )
                issue_credential_states_msg = json.loads(wh_text)
                if "StateID" in issue_credential_states_msg["message"]:
                    resp_json["state"] = self.issueCredentialStateTranslationDict[
                        issue_credential_states_msg["message"]["StateID"]
                    ]
                else:
                    raise Exception(
                        f"Could not retieve State from webhook message: {issue_credential_states_msg}"
                    )

                # Need a Credential_id in the response.
                # TODO Test is expecting format like indy, etc to contain the credential_id, Get it from the Last Webhook
                if "formats" in issue_credential_states_msg["message"]["Message"]:
                    format = issue_credential_states_msg["message"]["Message"][
                        "formats"
                    ][0]["format"]
                    format = self.CredentialFromatTranslationDict[format]
                    resp_json[format] = {"credential_id": record_id}
                else: # assume json-ld by default
                    resp_json["json-ld"] = {"credential_id": record_id}

                # This is is also the Name of the cred.
                resp_json["credential_id"] = record_id
                resp_text = json.dumps(resp_json)

            return (resp_status, resp_text)

        elif operation == "issue" and isWACI:
            # The data passed in to the handler here contains just the
            # Credential fulfillment attachment.
            # Below we arrange it as needed to be accepted by the AFGo agent's accept-request endpoint.

            data = {
                "issue_credential": {
                    "Type": "https://didcomm.org/issue-credential/3.0/issue-credential",
                    "ID": "1c60ffac-cd87-4433-9909-fa6e93431a14",
                    "Comment": "",
                    "Attachments": data,
                    "GoalCode": "",
                    "ReplacementID": ""
                }
            }

            (wh_status, wh_text) = await self.request_response_issue_credential(
                rec_id=record_id, message_name="issue-credential-states-msg"
            )
            issue_credential_actions_msg = json.loads(wh_text)

            record_id = issue_credential_actions_msg["message"]["Properties"]["piid"]

            agent_operation = make_agent_operation(record_id)

            (resp_status, resp_text) = await self.admin_POST(agent_operation, data)
            log_msg(resp_status, resp_text)

            if resp_status == 200:
                resp_json = json.loads(resp_text)
                # Get the state form the webhook callback.
                if record_id == None:
                    if "piid" in resp_json:
                        record_id = resp_json["piid"]
                    else:
                        raise Exception(
                            f"No piid found to retrieve State from webhook message: {resp_text}"
                        )
                (wh_status, wh_text) = await self.request_response_issue_credential(
                    record_id
                )
                issue_credential_states_msg = json.loads(wh_text)
                if "StateID" in issue_credential_states_msg["message"]:
                    resp_json["state"] = self.issueCredentialStateTranslationDict[
                        issue_credential_states_msg["message"]["StateID"]
                    ]
                else:
                    raise Exception(
                        f"Could not retrieve State from webhook message: {issue_credential_states_msg}"
                    )

                resp_text = json.dumps(resp_json)

            return (resp_status, resp_text)


        elif operation == "issue":
            cred = {}

            # TODO Need to get their DID to add to the data. Dummy input for now, which works fine.
            # Get data from the last issue-credential_states webhook message which contrains the credential_proposal
            if data is None or "issue_credential" not in data:
                # get the credential_proposal from the webhook
                if record_id is None:
                    raise Exception(
                        f"Have not passed a thread id for issuecredential/{command.operation}"
                    )

                (wh_status, wh_text) = await self.request_response_issue_credential(
                    rec_id=record_id, message_name="issue-credential-states-msg"
                )
                log_msg(f"Credential Data retreived from webhook message: ", wh_text)

                issue_credential_states_msg = json.loads(wh_text)
                record_id = issue_credential_states_msg["message"]["Properties"]["piid"]

                # if the messsage doesn't contain credential details get it from the credential_details_msg
                if "filters~attach" not in wh_text:
                    issue_credential_states_msg = pop_resource(
                        record_id, "credential-details-msg"
                    )
                    wh_text = json.dumps(issue_credential_states_msg)
                    log_msg(f"Credential Data retreived from details message: ", wh_text)

                # Format the proposal for afgo issue
                # suppliment the message data with whatever afgo needs to make the store credential work
                # IMO this is a defect in afgo
                if topic == "issue-credential-v2" or topic == "issue-credential-v3":
                    src_msg = issue_credential_states_msg["message"]["Message"]

                    cred_attachments = []
                    if "filters~attach" in src_msg:
                        cred_attachments = src_msg["filters~attach"]
                    else:
                        cred_attachments = src_msg["attachments"]

                    cred_formats = []
                    if "formats" in src_msg:
                        cred_formats = src_msg["formats"]

                    data = {
                        "issue_credential": {
                            "credentials~attach": cred_attachments,
                            "formats": cred_formats,
                        }
                    }

                    (
                        orb_did_status,
                        orb_did_text,
                        priv_key_kids,
                    ) = await self.get_orb_did()
                    if orb_did_status != 200:
                        print(
                            f"Couldn't retrieve my public did: status={orb_did_status} body={orb_did_text}"
                        )

                    for dat in data["issue_credential"]["credentials~attach"]:
                        if "json" in dat["data"]:
                            cred = dat["data"]["json"]
                        elif "base64" in dat["data"]:
                            dat_dec = base64.b64decode(dat["data"]["base64"])
                            cred = json.loads(dat_dec)
                            del dat["data"]["base64"]
                        else:
                            cred = {}

                        if "indy" in cred:
                            cred["@context"] = []
                            cred["credentialSubject"] = {}
                            cred["issuanceDate"] = (
                                str(
                                    datetime.datetime.now().isoformat(
                                        timespec="seconds"
                                    )
                                )
                                + "Z"
                            )
                            cred["issuer"] = {
                                "id": json.loads(wh_text)["message"]["Properties"][
                                    "myDID"
                                ]
                            }

                            cred["type"] = [
                                "VerifiableCredential",
                                "AATHTestCredential",
                            ]

                            dat["data"]["json"] = cred

                        else:
                            # handle json-ld creds that might or might not be in a "json-ld" field of the attachment
                            # TODO: we need a better way to distinguish indy and json-ld creds for the backchannel
                            if "json-ld" in cred:
                                cred = cred["json-ld"]

                            if "options" in cred:
                                options = cred["options"]
                            else:
                                options = {}

                            if "credential" in cred:
                                cred = cred["credential"]

                            # datetime in iso 8601 format, satisfies ietf rfc3339 so afgo can parse it from json
                            created_datetime = (
                                str(
                                    datetime.datetime.now()
                                    .replace(microsecond=0)
                                    .isoformat(timespec="seconds")
                                )
                                + "Z"
                            )

                            cred_type = cred["type"]

                            proof_type = options.get("proofType", "")

                            if self.myKeyId:
                                my_pub_did = cred["issuer"] if isinstance(cred["issuer"], str) else cred["issuer"]["id"]
                                selected_kid = self.myKeyId
                            else:
                                selected_kid = priv_key_kids.get(proof_type, "")
                                my_pub_did = json.loads(orb_did_text)["did"]

                            # signatureRepresentation is an integer code used in afgo
                            # to indicate the representation of the signature
                            # 0: proofValue
                            # 1: jws
                            # ed25519 uses jws, bbs+ uses proofValue
                            if proof_type == "Ed25519Signature2018":
                                signature_representation = 1
                            else:
                                signature_representation = 0

                            # sign credential
                            sign_cred_endpoint = "/verifiable/signcredential"
                            sign_cred_req = {
                                "did": my_pub_did,
                                "created": created_datetime,
                                "kid": selected_kid,
                                "signatureType": proof_type,
                                "signatureRepresentation": signature_representation,
                                "credential": cred,
                            }

                            (resp_status, resp_text) = await self.admin_POST(
                                sign_cred_endpoint, sign_cred_req
                            )
                            if resp_status != 200:
                                log_msg(
                                    f"failed to sign credential: status={resp_status}, data={resp_text}"
                                )
                                return (resp_status, resp_text)

                            sign_cred_resp = json.loads(resp_text)

                            cred = sign_cred_resp["verifiableCredential"]

                            # workaround for acapy being overly strict (requiring type be a list, in excess of the spec)
                            cred["type"] = cred_type

                            # convert base64-url to standard base64 for acapy's sake
                            if "proofValue" in cred["proof"]:
                                cred["proof"]["proofValue"] = (
                                    cred["proof"]["proofValue"]
                                    .replace("-", "+")
                                    .replace("_", "/")
                                )

                            dat["data"]["json"] = cred

                else:
                    data = {
                        "issue_credential": {
                            "credentials~attach": [
                                {
                                    "data": {
                                        "json": {
                                            "@context": [],
                                            "credentialSubject": {},
                                            "issuanceDate": str(
                                                datetime.datetime.now().isoformat(
                                                    timespec="seconds"
                                                )
                                            )
                                                + "Z",
                                            "issuer": {"id": self.myDID},
                                            "type": [
                                                "VerifiableCredential",
                                                "AATHTestCredential",
                                            ],
                                        }
                                    }
                                }
                            ]
                        }
                    }

            agent_operation = make_agent_operation(record_id)

            log_msg(
                f"Data translated by backchannel to send to agent for operation: {agent_operation}",
                data,
            )

            (resp_status, resp_text) = await self.admin_POST(agent_operation, data)
            log_msg(resp_status, resp_text)

            if resp_status == 200:
                resp_json = json.loads(resp_text)
                # Get the state form the webhook callback.
                if record_id == None:
                    if "piid" in resp_json:
                        record_id = resp_json["piid"]
                    else:
                        raise Exception(
                            f"No piid found to retrieve State from webhook message: {resp_text}"
                        )
                (wh_status, wh_text) = await self.request_response_issue_credential(
                    record_id
                )
                issue_credential_states_msg = json.loads(wh_text)
                if "StateID" in issue_credential_states_msg["message"]:
                    resp_json["state"] = self.issueCredentialStateTranslationDict[
                        issue_credential_states_msg["message"]["StateID"]
                    ]
                else:
                    raise Exception(
                        f"Could not retrieve State from webhook message: {issue_credential_states_msg}"
                    )

                resp_text = json.dumps(resp_json)

            return (resp_status, resp_text)


        # Make Special provisions for revoke since it is passing multiple query params not just one id.
        elif operation == "revoke":
            cred_rev_id = record_id
            rev_reg_id = data["rev_registry_id"]
            publish = data["publish_immediately"]
            agent_operation = (
                "/issue-credential/"
                + operation
                + "?cred_rev_id="
                + cred_rev_id
                + "&rev_reg_id="
                + rev_reg_id
                + "&publish="
                + str(publish).lower()
            )
            data = None

        log_msg(agent_operation, data)

        (resp_status, resp_text) = await self.admin_POST(agent_operation, data)

        log_msg(resp_status, resp_text)
        if resp_status == 200:
            resp_text = self.agent_state_translation(command.topic, None, resp_text)
        return (resp_status, resp_text)

    async def handle_present_proof_POST(self, command: BackchannelCommand):
        topic = command.topic
        operation = command.operation
        record_id = command.record_id
        data = command.data

        if record_id is None:
            agent_operation = f"{self.TopicTranslationDict[topic]}{self.proofOperationTranslationDict[operation]}"
        else:
            agent_operation = (
                self.TopicTranslationDict[topic]
                + record_id
                + "/"
                + self.proofOperationTranslationDict[operation]
            )

        if data is not None:
            log_msg(
                f"Data passed to backchannel by test for operation: {agent_operation}",
                data,
            )

        await self.load_jsonld_contexts()

        if operation == "send-request":
            # Get myDID and theirDID from connection object from connection_id in data
            (their_did, my_did) = await self.get_DIDs_for_participants(
                data["presentation_request"]["connection_id"]
            )
            # store off myDID incase it is needed later.
            self.myDID = my_did

            # create extra fields needed in presentation
            attach_id = str(uuid.uuid1())
            if "indy" in data["presentation_request"]["format"]:
                format_key = "hlindy/proof-req@v2.0"
                mime_type = "application/json"
            elif (
                "json_ld" in data["presentation_request"]["format"]
                or "json-ld" in data["presentation_request"]["format"]
            ):
                format_key = "dif/presentation-exchange/definitions@v1.0"
                mime_type = "application/ld+json"

                # await self.load_jsonld_contexts()

            else:
                raise Exception(f"format not recognized: {data}")

            # Create "request_presentation"
            # TODO for multiformat presentations will have to iterate over the data to figure out how many
            # right now we support 1 format
            data = {
                "my_did": my_did,
                "their_did": their_did,
                "request_presentation": {
                    "@type": "https://didcomm.org/present-proof/2.0/request-presentation",
                    "comment": data["presentation_request"]["comment"],
                    "formats": [{"attach_id": attach_id, "format": format_key}],
                    "request_presentations~attach": [
                        {
                            "@id": attach_id,
                            "data": {"json": data["presentation_request"]["data"]},
                            "mime-type": mime_type,
                        }
                    ],
                    "will_confirm": True,  # not sure we need this
                },
            }

        elif operation == "send-presentation":
            # Get the presentation details from the webook data
            (wh_status, wh_text) = await self.request_response_present_proof(
                command, message_name="present-proof-actions-msg"
            )
            if wh_status == 200 and wh_text is not None:
                present_proof_msg = json.loads(wh_text)
            else:
                raise Exception(
                    f"Could not retieve presentation information from webhook message for operation: {agent_operation}"
                )

            # Prepare the payload from the webhook data
            ammended_data = {
                "presentation": present_proof_msg["message"]["Message"],
                "piid": present_proof_msg["message"]["Message"]["@id"],
            }

            ammended_data["presentation"][
                "@type"
            ] = "https://didcomm.org/present-proof/2.0/presentation"
            ammended_data["presentation"]["presentations~attach"] = ammended_data[
                "presentation"
            ]["request_presentations~attach"]
            ammended_data["presentation"].pop("request_presentations~attach", None)
            ammended_data["presentation"].pop("~thread", None)
            ammended_data["presentation"].pop("will_confirm", None)
            ammended_data["presentation"]["presentations~attach"][0]["data"][
                "json"
            ] = data

            ammended_data["presentation"]["presentations~attach"][0]["data"]["json"][
                "@context"
            ] = ["https://www.w3.org/2018/credentials/v1"]
            ammended_data["presentation"]["presentations~attach"][0]["data"]["json"][
                "type"
            ] = ["VerifiablePresentation", "CredentialManagerPresentation"]

            ammended_data["presentation"][
                "request_presentations~attach"
            ] = ammended_data["presentation"]["presentations~attach"]

            if "json_ld" in data["format"] or "json-ld" in data["format"]:

                cred_attach_list = []

                if "record_ids" in data:
                    for record_id_list in data["record_ids"].values():
                        for record_id in record_id_list:
                            cred_record_list = get_resource(
                                record_id, "credential-cache-msg"
                            )

                            if len(cred_record_list) > 0:
                                cred_attachments = cred_record_list[-1]["message"][
                                    "Message"
                                ]["credentials~attach"]
                                for cred_attach in cred_attachments:
                                    cred_attach_list.append(cred_attach)

                for cred_attach in cred_attach_list:
                    cred_attach["mime-type"] = "application/ld+json"

                    if (
                        "json" in cred_attach["data"]
                        and "json-ld" in cred_attach["data"]["json"]
                    ):
                        # merge the cred proper with its wrapping
                        cred_attach["data"]["json"]["json-ld"]["credential"][
                            "issuer"
                        ] = cred_attach["data"]["json"]["issuer"]
                        cred_attach["data"]["json"]["json-ld"]["credential"][
                            "issuanceDate"
                        ] = cred_attach["data"]["json"]["issuanceDate"]

                        cred_attach["data"]["json"] = cred_attach["data"]["json"][
                            "json-ld"
                        ]["credential"]

                ammended_data["presentation"]["presentations~attach"] = cred_attach_list

            data = ammended_data

        elif operation == "verify-presentation":

            data = {"names": [record_id]}

        log_msg(
            f"Data translated by backchannel to send to agent for operation: {agent_operation}",
            data,
        )

        (resp_status, resp_text) = await self.admin_POST(agent_operation, data)
        resp_json = json.loads(resp_text)

        if resp_status == 200:
            if operation == "send-request":
                # set a thread_id for the test harness
                if "piid" in resp_json:
                    resp_json["thread_id"] = resp_json["piid"]
                else:
                    raise Exception(
                        f"No piid(thread_id) found in response for operation: {agent_operation} {resp_text}"
                    )

            # The response doesn't have a state. Get it from the present_proof_states webhook message
            if "piid" in resp_json:
                wh_id = resp_json["piid"]
            else:
                wh_id = record_id
            await asyncio.sleep(1)
            present_proof_states_msg = pop_resource_latest("present-proof-states-msg")
            # present_proof_states_msg = json.loads(wh_text)
            if "StateID" in present_proof_states_msg["message"]:
                resp_json["state"] = present_proof_states_msg["message"]["StateID"]
            else:
                raise Exception(
                    f"Could not retieve State from webhook message: {present_proof_states_msg}"
                )
            resp_text = json.dumps(resp_json)

        log_msg(resp_status, resp_text)
        if resp_status == 200:
            resp_text = self.agent_state_translation(
                command.topic, operation, resp_text
            )
        return (resp_status, resp_text)

    async def handle_present_proof_v3_POST(self, command: BackchannelCommand):
        topic = command.topic
        operation = command.operation
        record_id = command.record_id
        data = command.data

        def get_agent_operation_path(record_id: str, operation: str):
            if record_id is None:
                return f"{self.TopicTranslationDict[topic]}{self.proofOperationTranslationDict[operation]}"
            else:
                return (
                    self.TopicTranslationDict[topic]
                    + record_id
                    + "/"
                    + self.proofOperationTranslationDict[operation]
                )

        agent_operation = get_agent_operation_path(record_id, operation)

        if data is not None:
            log_msg(
                f"Data passed to backchannel by test for operation: {agent_operation}",
                data,
            )

        await self.load_jsonld_contexts()

        if operation == "send-proposal":
            data = {
                "connection_id": data["presentation_proposal"]["connection_id"],
                "propose_presentation": {
                    "type": "https://didcomm.org/present-proof/3.0/propose-presentation",
                    "body": {
                        "comment": data["presentation_proposal"]["comment"],
                    },
                },
            }

        if operation == "send-request":
            # create extra fields needed in presentation
            attach_id = str(uuid.uuid1())
            if (
                "json_ld" in data["presentation_request"]["format"]
                or "json-ld" in data["presentation_request"]["format"]
            ):
                format_key = "dif/presentation-exchange/definitions@v1.0"
                mime_type = "application/ld+json"
            else:
                raise Exception(f"format not supported for present-proof v3: {data}")

            amended_data = {
                "request_presentation": {
                    "type": "https://didcomm.org/present-proof/3.0/request-presentation",
                    "body": {
                        "comment": data["presentation_request"]["comment"],
                    },
                    "attachments": [
                        {
                            "id": attach_id,
                            "format": format_key,
                            "data": {"json": data["presentation_request"]["data"]},
                            "mime-type": mime_type,
                        }
                    ],
                },
            }

            if "connection_id" in amended_data:
                amended_data["connection_id"] = data["connection_id"]
            else: # use afgo's accept-propose-presentation command
                operation = "accept-proposal"
                agent_operation = get_agent_operation_path(record_id, operation)

            data = amended_data

        elif operation == "send-presentation":
            # Get the presentation details from the webook data
            (wh_status, wh_text) = await self.request_response_present_proof(
                command, message_name="present-proof-actions-msg"
            )
            if wh_status != 200 or wh_text is None:
                raise Exception(
                    f"Could not retieve presentation information from webhook message for operation: {agent_operation}"
                )

            present_proof_msg = json.loads(wh_text)

            piid = present_proof_msg["message"]["Properties"]["piid"]

            presentation = present_proof_msg["message"]["Message"]

            presentation["type"] = "https://didcomm.org/present-proof/3.0/presentation"

            presentation.pop("request_presentations~attach", None)
            presentation.pop("attachments", None)
            presentation.pop("~thread", None)
            presentation.pop("will_confirm", None)

            if "json_ld" in data["format"] or "json-ld" in data["format"]:

                cred_attach_list = []

                if "record_ids" in data:
                    for record_id_list in data["record_ids"].values():
                        for record_id in record_id_list:
                            cred_record_list = get_resource(
                                record_id, "credential-cache-msg"
                            )

                            if len(cred_record_list) > 0:
                                cred_attachments = cred_record_list[-1]["message"]["Message"]["attachments"]

                                for cred_attach in cred_attachments:
                                    cred_attach_list.append(cred_attach)

                for cred_attach in cred_attach_list:
                    cred_attach["media_type"] = "application/ld+json"

                    if (
                        "json" in cred_attach["data"]
                        and "json-ld" in cred_attach["data"]["json"]
                    ):
                        # merge the cred proper with its wrapping
                        cred_attach["data"]["json"]["json-ld"]["credential"][
                            "issuer"
                        ] = cred_attach["data"]["json"]["issuer"]
                        cred_attach["data"]["json"]["json-ld"]["credential"][
                            "issuanceDate"
                        ] = cred_attach["data"]["json"]["issuanceDate"]

                        cred_attach["data"]["json"] = cred_attach["data"]["json"][
                            "json-ld"
                        ]["credential"]

                presentation["attachments"] = cred_attach_list

            data = {
                "presentation": presentation,
                "piid": piid,
            }

        elif operation == "verify-presentation":

            data = {"names": [record_id]}

        log_msg(
            f"Data translated by backchannel to send to agent for operation: {agent_operation}",
            data,
        )

        (resp_status, resp_text) = await self.admin_POST(agent_operation, data)

        if resp_status!= 200:
            log_msg(resp_status, resp_text)
            return (resp_status, resp_text)

        resp_json = json.loads(resp_text)

        if operation == "send-request" or operation == "send-proposal":
            # set a thread_id for the test harness
            if "piid" in resp_json:
                resp_json["thread_id"] = resp_json["piid"]
            else:
                raise Exception(
                    f"No piid(thread_id) found in response for operation: {agent_operation} {resp_text}"
                )

        # The response doesn't have a state. Get it from the present_proof_states webhook message
        await asyncio.sleep(1)
        present_proof_states_msg = pop_resource_latest("present-proof-states-msg")
        # present_proof_states_msg = json.loads(wh_text)
        if "StateID" in present_proof_states_msg["message"]:
            resp_json["state"] = present_proof_states_msg["message"]["StateID"]
        else:
            raise Exception(
                f"Could not retieve State from webhook message: {present_proof_states_msg}"
            )
        resp_text = json.dumps(resp_json)

        log_msg(resp_status, resp_text)

        if resp_status == 200:
            resp_text = self.agent_state_translation(
                command.topic, operation, resp_text
            )
        return (resp_status, resp_text)

    async def load_jsonld_contexts(self):
        if not hasattr(self, "loaded_jsonld_contexts"):
            self.loaded_jsonld_contexts = []

        context_data = [
            {
                "url": "https://w3id.org/citizenship/v1",
                "documentURL": "https://w3c-ccg.github.io/citizenship-vocab/contexts/citizenship-v1.jsonld",
                "filePath": "afgo/citizenship-v1.jsonld",
            }
        ]

        req = {"documents": []}

        should_post = False

        for jsonld_context in context_data:
            if jsonld_context["url"] not in self.loaded_jsonld_contexts:
                req_doc = {
                    "url": jsonld_context["url"],
                    "documentURL": jsonld_context["documentURL"],
                }

                with open(jsonld_context["filePath"], "r") as in_file:
                    schema_text = in_file.read()
                    req_doc["content"] = json.loads(schema_text)

                req["documents"].append(req_doc)

                should_post = True
                self.loaded_jsonld_contexts.append(jsonld_context["url"])

        if should_post:
            (resp_status, resp_text) = await self.admin_POST("/ld/context", data=req)
            if resp_status != 200:
                print("failed: add json-ld contexts")
                raise Exception(f"Could not add contexts: {resp_text}")
            else:
                print("success: add json-ld contexts")
        else:
            print("skipped: add json-ld contexts")

    def add_did_exchange_state_to_response(self, operation: str, raw_response: str):
        resp_json = json.loads(raw_response)

        if operation == "send-response":
            resp_json["state"] = "response-sent"
        elif operation == "send-message":
            resp_json["state"] = "request-sent"

        return json.dumps(resp_json)

    async def make_agent_GET_request(
        self,
        command: BackchannelCommand,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[int, str]:
        record_id = command.record_id

        if command.topic == "status":
            status = 200 if self.ACTIVE else 418
            status_msg = "Active" if self.ACTIVE else "Inactive"
            return (status, json.dumps({"status": status_msg}))

        if command.topic == "version":
            if self.afgo_version is not None:
                status = 200
                status_msg = self.afgo_version
            else:
                status = 200
                status_msg = "unknown"
            return (status, status_msg)

        elif command.topic == "connection" or command.topic == "did-exchange":
            if record_id:
                connection_id = record_id
                agent_operation = f"/connections/{connection_id}"
            else:
                agent_operation = "/connections"

            log_msg("GET Request agent operation: ", agent_operation)

            (resp_status, resp_text) = await self.admin_GET(
                agent_operation, params=params
            )
            if resp_status != 200:
                return (resp_status, resp_text)

            log_msg("GET Request response details: ", resp_status, resp_text)

            resp_json = json.loads(resp_text)
            if len(resp_json) != 0:
                if record_id:
                    connection_info = {
                        "connection_id": resp_json["result"]["ConnectionID"],
                        "state": resp_json["result"]["State"],
                        "connection": resp_json,
                    }
                    resp_text = json.dumps(connection_info)
                else:
                    resp_json = resp_json["results"]
                    connection_infos = []
                    for connection in resp_json:
                        connection_info = {
                            "connection_id": connection["ConnectionID"],
                            "state": connection["State"],
                            "connection": connection,
                        }
                        connection_infos.append(connection_info)
                    resp_text = json.dumps(connection_infos)
                # translate the state from that the agent gave to what the tests expect
                resp_text = self.agent_state_translation(command.topic, None, resp_text)
            return (resp_status, resp_text)

        elif command.topic == "did":
            (resp_status, resp_text, resp_kids) = await self.get_orb_did()
            return (resp_status, resp_text)

        elif command.topic == "schema":
            # afgo does not support indy schema. Return dummy schema
            schema = {"id": "did:", "name": "", "version": self.afgo_version}
            return (200, json.dumps(schema))

        elif command.topic == "credential-definition":
            # afgo does not support indy schema. Return dummy id
            resp_json = {"id": None}
            return (200, json.dumps(resp_json))

        elif (
            command.topic == "issue-credential"
            or command.topic == "issue-credential-v2"
            or command.topic == "issue-credential-v3"
        ):
            if command.record_id == "retrieve-credential-proposal":
                propose_credential_message_from_holder = get_resource_latest("issue-credential-actions-msg")

                propose_credential_message = propose_credential_message_from_holder["message"]["Message"]

                return 200, json.dumps(propose_credential_message)

            elif command.record_id == "retrieve-credential-application":
                request_credential_message_from_holder = get_resource_latest("issue-credential-actions-msg")

                credential_application_attachment = \
                    request_credential_message_from_holder["message"]["Message"]["attachments"][0]["data"]["json"]

                return 200, json.dumps(credential_application_attachment)

            (wh_status, wh_text) = await self.request_response_issue_credential(
                record_id
            )
            issue_credential_states_msg = json.loads(wh_text)
            if "StateID" in issue_credential_states_msg["message"]:
                resp_json = {"state": issue_credential_states_msg["message"]["StateID"]}
            else:
                raise Exception(
                    f"Could not retieve State from webhook message: {issue_credential_states_msg}"
                )
            return (200, json.dumps(resp_json))

        elif command.topic == "credential":
            operation = command.operation
            if operation == "revoked":
                agent_operation = f"/credential/{operation}/{record_id}"
            else:
                agent_operation = f"/verifiable/credential/name/{record_id}"

            # No quivalent GET in afgo
            # afgo only provides /actions GET
            (resp_status, resp_text) = await self.admin_GET(agent_operation)
            if resp_status == 200:
                resp_json = json.loads(resp_text)
                # take the name (which was saved as the cred_id) and make it the referent
                if "name" in resp_json:
                    resp_json["referent"] = resp_json["name"]
                    resp_json["credential_id"] = resp_json["name"]
                    resp_text = json.dumps(resp_json)
                else:
                    raise Exception(
                        f"No name/id found in response for: {agent_operation}"
                    )
            return (resp_status, resp_text)

        elif command.topic == "proof" or command.topic == "proof-v2" or command.topic == "proof-v3":
            present_proof_states_msg = await pop_message_stack(
                    "present-proof-states-msg" + "," + command.record_id, MAX_TIMEOUT
            )

            # (wh_status, wh_text) = await self.request_response_present_proof(command)
            # present_proof_states_msg = json.loads(wh_text)
            if "StateID" in present_proof_states_msg["message"]:
                resp_json = {"state": present_proof_states_msg["message"]["StateID"]}
            else:
                raise Exception(
                    f"Could not retieve State from webhook message: {present_proof_states_msg}"
                )

            print("GET proof state response: " + json.dumps(resp_json))

            return (200, json.dumps(resp_json))

        elif command.topic == "revocation":
            # afgo does not support indy revocation. Return dummy data
            schema = {"indy_revocation": "not supported by AFGO"}
            return (200, json.dumps(schema))

        elif command.topic == "oob-v2":
            (resp_status, resp_text) = await self.handle_oob_v2_GET(command)
            return (resp_status, resp_text)

        return (501, "501: Not Implemented\n\n")

    async def get_orb_did(self) -> Tuple[int, str, dict]:
        agent_operation = "/vdr/did"

        agent_name = os.getenv("AGENT_NAME")
        orb_did_path = f"/data-mount/orb-dids/{agent_name}.json"

        orb_did_name = os.getenv("AFGO_ORBDID_NAME")
        if orb_did_name is None or len(orb_did_name) == 0:
            orb_did_name = "<default orb did>"

        with open(orb_did_path) as orb_did_file:
            orb_did = orb_did_file.read()
            orb_did_json = json.loads(orb_did)
            (resp_status, resp_text) = await self.admin_POST(
                agent_operation, data={"did": orb_did_json, "name": orb_did_name}
            )
        if resp_status != 200 and resp_status != 400:
            return (resp_status, resp_text, {})

        # import the ed25519 and Bls private keys for orb did
        priv_key_path = os.getenv("AFGO_ORBDID_PRIVKEY")

        kid_map = {}

        with open(priv_key_path) as priv_key_file:
            priv_keys = priv_key_file.read()
            priv_key_set = json.loads(priv_keys)
            for signature_type, priv_key_json in priv_key_set.items():
                priv_key_kid = ""
                if "kid" in priv_key_json:
                    priv_key_kid = priv_key_json["kid"]

                (resp_status, resp_text) = await self.admin_POST(
                    "/kms/import", data=priv_key_json
                )
                if resp_status != 200:
                    print(
                        f"failed to import private key: status={resp_status} body={resp_text}"
                    )
                    if resp_status == 500 and "already exists" in resp_text:
                        resp_status = 200  # it's fine if we already created the key
                    else:
                        return (resp_status, resp_text, {})

                kid_map[signature_type] = priv_key_kid

        return (resp_status, json.dumps({"did": orb_did_json["id"]}), kid_map)

    async def make_agent_DELETE_request(
        self, command: BackchannelCommand
    ) -> Tuple[int, str]:
        record_id = command.record_id

        if command.topic == "credential" and record_id:
            agent_operation = f"/credential/{record_id}"
            log_msg(agent_operation)

            (resp_status, resp_text) = await self.admin_DELETE(agent_operation)
            if resp_status == 200:
                resp_text = self.agent_state_translation(command.topic, None, resp_text)
            return (resp_status, resp_text)

        return (501, "501: Not Implemented\n\n")

    async def request_response_connection(self, rec_id: str) -> Tuple[int, str]:
        # TODO: no result will ever be found, since nothing ever pushes 'connection-msg'
        connection_msg = pop_resource(rec_id, "connection-msg")
        i = 0
        while connection_msg is None and i < MAX_TIMEOUT:
            await asyncio.sleep(1)
            connection_msg = pop_resource(rec_id, "connection-msg")
            i = i + 1

        resp_status = 200
        if connection_msg:
            resp_text = json.dumps(connection_msg)
        else:
            resp_text = "{}"

        return (resp_status, resp_text)

    async def request_response_did_exchange(
        self, rec_id: Optional[str] = None
    ) -> Tuple[int, str]:
        if rec_id:
            message_type = "didexchange-states-msg" + "," + rec_id
            try:
                didexchange_msg = await pop_message_queue(message_type, MAX_TIMEOUT)
            except:
                print("didex timeout waiting for didexchange-states-msg")
                return (200, "{}")
        else:
            try:
                # fallback: check last message if none is available under rec_id
                # for implicit invitation the harness can't pass in the invitation ID
                await asyncio.sleep(2)
                didexchange_msg = await pop_message_stack(
                    "didexchange-states-msg", MAX_TIMEOUT
                )
            except:
                print("didex timeout waiting for didexchange-states-msg fallback")
                return (200, "{}")

        resp_status = 200
        if didexchange_msg:
            resp_text = json.dumps(didexchange_msg)
            resp_text = self.agent_state_translation("did-exchange", None, resp_text)

            if "message" in didexchange_msg:
                conn_id = didexchange_msg["message"]["Properties"]["connectionID"]
                resp_text = json.dumps(
                    {"connection_id": conn_id, "data": didexchange_msg}
                )

        else:
            print("didex NO RESULT FOUND for didexchange-states-msg")
            resp_text = "{}"

        return (resp_status, resp_text)

    async def request_response_out_of_band(self, rec_id: str) -> Tuple[int, str]:
        # TODO: no result will ever be found, since nothing ever pushes 'didexchange-msg'
        c_msg = pop_resource(rec_id, "didexchange-msg")
        i = 0
        while didexchange_msg is None and i < MAX_TIMEOUT:
            await asyncio.sleep(1)
            didexchange_msg = pop_resource(rec_id, "didexchange-msg")
            i = i + 1

        resp_status = 200
        if didexchange_msg:
            resp_text = json.dumps(didexchange_msg)
            resp_text = self.agent_state_translation("out-of-band", None, resp_text)

            if "message" in didexchange_msg:
                conn_id = didexchange_msg["message"]["Properties"]["connectionID"]
                resp_text = json.dumps(
                    {"connection_id": conn_id, "data": didexchange_msg}
                )

        else:
            resp_text = "{}"

        return (resp_status, resp_text)

    async def request_response_issue_credential(
        self, rec_id: str, message_name: Optional[str] = None
    ) -> Tuple[int, str]:
        if message_name is None:
            message_name = "issue-credential-states-msg"
        await asyncio.sleep(1)

        credential_msg = pop_resource_latest(message_name)
        i = 0
        while credential_msg is None and i < MAX_TIMEOUT:
            await asyncio.sleep(1)
            credential_msg = pop_resource_latest(message_name)
            i = i + 1

        # If we couldn't get a state out of the states webhook message, see if we can get the type and determine what the
        # state should be. This is a guess as afgo doesn't return states to receivers.
        if (message_name == "issue-credential-states-msg") and (
            credential_msg == None or "message" not in credential_msg
        ):
            message_name = "issue-credential-actions-msg"
            credential_msg = get_resource_latest(message_name)
            i = 0
            while credential_msg is None and i < MAX_TIMEOUT:
                await asyncio.sleep(1)
                # TODO May need to get instead of pop because the msg may be needed elsewhere.
                # credential_msg = pop_resource_latest(message_name)
                credential_msg = get_resource_latest(message_name)
                i = i + 1
            if "message" in credential_msg:
                op_type = credential_msg["message"]["Message"]["@type"]
                state = self.IssueCredentialTypeToStateTranslationDict[op_type]
                credential_msg["message"]["StateID"] = state
                credential_msg["state"] = state
            else:
                raise Exception(
                    f"Could not retieve State from webhook message: {issue_credential_actions_msg}"
                )

        # There is an issue with the issue command and it needs the credential~attach as well as the thread_id
        # Because we are popping the webhook off the stack because we are getting the protocol state we are losing
        # the credential details (it isn't contained in every webhook message), and it is no longer being sent by
        # the tests. So, if the credential message contains the full credential like filters~attach, then re-add
        # it to the stack again keyed by the piid called credential_details_msg. This way if any call has a problem
        # getting the cred details from the webhook messages, we have it here to fall back on.
        credential_msg_txt = json.dumps(credential_msg)
        if "filters~attach" in credential_msg_txt or "/3.0/propose-credential" in credential_msg_txt:
            thread_id = credential_msg["message"]["Properties"]["piid"]
            push_resource(thread_id, "credential-details-msg", credential_msg)
            log_msg(
                f"Added credential details back into webhook storage: {json.dumps(credential_msg)}"
            )
        if "credentials~attach" in credential_msg_txt or "/3.0/issue-credential" in credential_msg_txt:
            thread_id = credential_msg["message"]["Properties"]["piid"]
            push_resource(thread_id, "credential-cache-msg", credential_msg)
            log_msg(
                f"Added credential details back into webhook storage: {json.dumps(credential_msg)}"
            )

        resp_status = 200
        if credential_msg:
            resp_text = json.dumps(credential_msg)
        else:
            resp_text = "{}"

        return (resp_status, resp_text)

    async def request_response_credential(self, rec_id: str) -> Tuple[int, str]:
        credential_msg = pop_resource(rec_id, "credential-msg")
        i = 0
        while credential_msg is None and i < MAX_TIMEOUT:
            await asyncio.sleep(1)
            credential_msg = pop_resource(rec_id, "credential-msg")
            i = i + 1

        resp_status = 200
        if credential_msg:
            resp_text = json.dumps(credential_msg)
        else:
            resp_text = "{}"

        return (resp_status, resp_text)

    async def request_response_present_proof(
        self, command: BackchannelCommand, message_name: Optional[str] = None
    ) -> Tuple[int, str]:
        if message_name is None:
            message_name = "present-proof-states-msg"

        await asyncio.sleep(1)
        presentation_msg = pop_resource(command.record_id, message_name)
        i = 0
        while presentation_msg is None and i < MAX_TIMEOUT:
            await asyncio.sleep(1)
            presentation_msg = pop_resource(command.record_id, message_name)
            i = i + 1

        # If we couldn't get a state out of the states webhook message, see if we can get the type and determine what the
        # state should be. This is a guess as afgo doesn't return states to receivers.
        if (message_name == "present-proof-states-msg") and (
            presentation_msg == None or "message" not in presentation_msg
        ):
            message_name = "present-proof-actions-msg"
            presentation_msg = get_resource_latest(message_name)
            i = 0
            while presentation_msg is None and i < MAX_TIMEOUT:
                await asyncio.sleep(1)
                # TODO May need to get instead of pop because the msg may be needed elsewhere.
                # credential_msg = pop_resource_latest(message_name)
                presentation_msg = get_resource_latest(message_name)
                i = i + 1
            if "message" in presentation_msg:
                op_type = presentation_msg["message"]["Message"]["@type"]
                state = self.ProofTypeToStateTranslationDict[op_type]
                presentation_msg["message"]["StateID"] = state
                presentation_msg["state"] = state
            else:
                raise Exception(
                    f"Could not retieve State from webhook message: {presentation_msg}"
                )

        resp_status = 200
        if presentation_msg:
            resp_text = json.dumps(presentation_msg)
            if resp_status == 200:
                resp_text = self.agent_state_translation(command.topic, None, resp_text)
        else:
            resp_text = "{}"

        return (resp_status, resp_text)

    async def request_response_revocation_registry(
        self, rec_id: str
    ) -> Tuple[int, str]:
        revocation_msg = pop_resource(rec_id, "revocation-registry-msg")
        i = 0
        while revocation_msg is None and i < MAX_TIMEOUT:
            await asyncio.sleep(1)
            revocation_msg = pop_resource(rec_id, "revocation-registry-msg")
            i = i + 1

        resp_status = 200
        if revocation_msg:
            resp_text = json.dumps(revocation_msg)
        else:
            resp_text = "{}"

        return (resp_status, resp_text)

    async def make_agent_GET_request_response(
        self, command: BackchannelCommand, message_name: Optional[str] = None
    ) -> Tuple[int, str]:
        topic = command.topic
        record_id = command.record_id

        if topic == "connection" and record_id:
            return await self.request_response_connection(record_id)

        elif topic == "did":
            # TODO: change to actual method call
            return (200, "some stats")

        elif topic == "did-exchange":
            return await self.request_response_did_exchange(record_id)

        elif topic == "out-of-band" and record_id:
            return await self.request_response_out_of_band(record_id)

        elif (
            topic == "issue-credential" or topic == "issue-credential-v2" or topic == "issue-credential-v3"
        ) and record_id:
            return await self.request_response_issue_credential(
                record_id, message_name=message_name
            )

        elif topic == "credential" and record_id:
            return await self.request_response_credential(record_id)

        elif (topic == "proof" or topic == "proof-v2") and record_id:
            return await self.request_response_present_proof(
                command, message_name=message_name
            )

        elif topic == "revocation-registry" and record_id:
            return await self.request_response_revocation_registry(record_id)

        elif topic == "pass-registry" and record_id:
            pass

        return (501, "501: Not Implemented\n\n")

    def _process(
        self, args: List[str], env: Dict[str, str], loop: asyncio.AbstractEventLoop
    ):
        proc = subprocess.Popen(
            args,
            env=env,
            encoding="utf-8",
        )
        stdout = loop.run_in_executor(
            None,
            output_reader,
            proc.stdout,
            functools.partial(self.handle_output, source="stdout"),
        )
        stderr = loop.run_in_executor(
            None,
            output_reader,
            proc.stderr,
            functools.partial(self.handle_output, source="stderr"),
        )
        self.output_handler_futures = [stdout, stderr]
        return proc

    def get_process_args(self, bin_path: Optional[str] = None) -> List[str]:
        # TODO aries-agent-rest needs to be in the path so no need to give it a cmd_path
        cmd_path = "aries-agent-rest"
        if bin_path is None:
            bin_path = DEFAULT_BIN_PATH
        if bin_path:
            cmd_path = os.path.join(bin_path, cmd_path)
        print("Location of aries-agent-rest: " + cmd_path)
        return list(flatten(([cmd_path, "start"], self.get_agent_args())))

    async def detect_process(self):
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

        status_url = self.admin_url + "/connections"
        status_text = await fetch_swagger(status_url, START_TIMEOUT)
        print("Agent running with admin url", self.admin_url)

        if not status_text:
            raise Exception(
                "Timed out waiting for agent process to start. "
                + f"Admin URL: {status_url}"
            )

    async def start_process_with_extra_args(
        self, *, args: List[str] = [], bin_path: Optional[str] = None, wait: bool = True
    ):
        my_env = os.environ.copy()
        agent_args = self.get_process_args(bin_path) + args

        # start agent sub-process
        self.log(f"Starting agent sub-process ...")
        self.log(f"agent starting with params: ")
        self.log(agent_args)
        self.log("and environment:")
        self.log(my_env)
        loop = asyncio.get_event_loop()
        self.proc = await loop.run_in_executor(
            None, self._process, agent_args, my_env, loop
        )
        if wait:
            await asyncio.sleep(1.0)
            await self.detect_process()

    async def start_process(self, bin_path: str = None, wait: bool = True):
        my_env = os.environ.copy()

        # By default start agent with http inbound / outbound transport
        agent_args = self.get_process_args(bin_path) + self.get_host_args(
            inbound_transports=["http"], outbound_transports=["http"]
        )

        # start agent sub-process
        self.log(f"Starting agent sub-process ...")
        self.log(f"agent starting with params: ")
        self.log(agent_args)
        self.log("and environment:")
        self.log(my_env)
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

    async def kill_agent(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        if loop is None:
            loop = asyncio.get_event_loop()

        if self.proc:
            await loop.run_in_executor(None, self._terminate)

        for fut in self.output_handler_futures:
            fut.cancel()

        self.output_handler_futures = []

        # delete all backchannel metadata relating to data saved to agent
        self.loaded_jsonld_contexts = []

    async def terminate(self):
        await self.kill_agent()

        await self.client_session.close()
        if self.webhook_site:
            await self.webhook_site.stop()

    def agent_state_translation(self, topic: str, operation: Optional[str], data: str):
        # This method is used to translate the agent states passes back in the responses of operations into the states the
        # test harness expects. The test harness expects states to be as they are written in the Protocol's RFC.
        # the following is what the tests/rfc expect vs what afgo communicates
        # Connection Protocol:
        # Tests/RFC         |   Afgo
        # invited           |   invitation
        # requested         |   request
        # responded         |   response
        # complete          |   active
        #
        # Issue Credential Protocol:
        # Tests/RFC         |   Afgo
        # proposal-sent     |   proposal_sent
        # proposal-received |   proposal_received
        # offer-sent        |   offer_sent
        # offer_received    |   offer_received
        # request-sent      |   request_sent
        # request-received  |   request_received
        # credential-issued |   issued
        # credential-received | credential_received
        # done              |   credential_acked
        #
        # Present Proof Protocol:
        # Tests/RFC         |   Afgo

        def replace_state_values(data: str, *, old_state: str, new_state: str):
            return data.replace(f'"state": "{old_state}"', f'"state": "{new_state}"')

        resp_json = json.loads(data)

        # Check to see if state is in the json
        if "state" in resp_json:
            agent_state = resp_json["state"]

            if topic == "connection" or topic == "did-exchange":
                if operation == "send-request":
                    # We know this is the requester because we are in send-request, so swap for expected requester state
                    data = data.replace(
                        agent_state,
                        self.connectionRequesterStateTranslationDict[agent_state],
                    )
                elif operation == "send-response":
                    # The send response quickly goes to completed state. if completed in the send-reponse, just swap the
                    # state to response-sent.
                    if "completed" in data:
                        data = data.replace("completed", "response-sent")
                    else:
                        data = data.replace(
                            agent_state,
                            self.connectionResponderStateTranslationDict[agent_state],
                        )
                else:
                    data = data.replace(
                        agent_state,
                        self.connectionResponderStateTranslationDict[agent_state],
                    )
            elif topic == "issue-credential" or topic == "issue-credential-v2" or topic == "issue-credential-v3":
                data = data.replace(
                    agent_state, self.issueCredentialStateTranslationDict[agent_state]
                )
            elif topic == "proof" or topic == "proof-v2":
                data = replace_state_values(
                    data,
                    old_state=agent_state,
                    new_state=self.presentProofStateTranslationDict[agent_state],
                )
            elif topic == "out-of-band" or topic == "did-exchange":
                data = replace_state_values(
                    data,
                    old_state=agent_state,
                    new_state=self.connectionResponderStateTranslationDict[agent_state],
                )

        else:
            if topic == "out-of-band":
                if operation == "send-invitation-message":
                    resp_json["state"] = "invitation-sent"
                    resp_json[
                        "service"
                    ] = '["did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/didexchange/v1.0"]'
                    data = json.dumps(resp_json)

            elif topic == "proof" or topic == "proof-v2":
                if operation == "send-request":
                    data = json.dumps(resp_json)
                elif operation == "send-presentation":
                    data = json.dumps(resp_json)

        return data


async def main(start_port: int, show_timing: bool = False, interactive: bool = True):

    genesis = None
    agent = None

    agent_ports = AgentPorts(
        http=start_port + 1,
        admin=start_port + 2,
        # webhook listens on +3
        ws=start_port + 4,
    )

    try:
        agent = AfGoAgentBackchannel(
            "afgo",
            agent_ports=agent_ports,
            genesis_data=genesis,
        )

        # add mediation routes
        agent.app.add_routes(mediation_routes)

        # start backchannel (common across all types of agents)
        await agent.listen_backchannel(start_port)

        # start afgo agent sub-process and listen for web hooks
        await agent.listen_webhooks(start_port + 3)

        await agent.start_process()
        agent.activate()

        # now wait ...
        if interactive:
            async for option in prompt_loop("(X) Exit? [X] "):
                if option is None or option in "xX":
                    break
        else:
            print("Press Ctrl-C to exit ...")
            remaining_tasks = asyncio.all_tasks()
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
