import { Controller, Get, PathParams, Post, BodyParams } from "@tsed/common";
import { NotFound } from "@tsed/exceptions";
import {
  Agent,
  JsonTransformer,
  PresentationPreview,
  ProofRequest,
  RequestedCredentials,
} from "aries-framework-javascript";
import { ProofRecord } from "aries-framework-javascript/build/lib/storage/ProofRecord";
import { Body } from "node-fetch";

@Controller("/agent/command/proof")
export class PresentProofController {
  private agent: Agent;

  public constructor(agent: Agent) {
    this.agent = agent;
  }

  @Get("/:threadId")
  async getProofByThreadId(@PathParams("threadId") threadId: string) {
    const proofRecord = await this.agent.proof.getByThreadId(threadId);

    if (!proofRecord) {
      throw new NotFound(`proof record for thead id "${threadId}" not found.`);
    }

    return this.mapProofRecord(proofRecord);
  }

  @Get("/")
  async getAllProofs() {
    const proofs = await this.agent.proof.getAll();

    return proofs.map((proof) => this.mapProofRecord(proof));
  }

  @Post("/send-proposal")
  async sendProposal(
    @BodyParams("data")
    data: {
      connection_id: string;
      presentation_proposal: any;
    }
  ) {
    const presentationProposal = JsonTransformer.fromJSON(
      data.presentation_proposal,
      PresentationPreview
    );

    const proofRecord = await this.agent.proof.proposeProof(
      data.connection_id,
      presentationProposal,
      {
        comment: data.presentation_proposal.comment,
      }
    );

    return this.mapProofRecord(proofRecord);
  }

  @Post("/send-request")
  async sendRequest(
    @BodyParams("id") threadId: string,
    @BodyParams("data")
    data: {
      connection_id: string;
      presentation_proposal: any;
    }
  ) {
    const proofRequest = JsonTransformer.fromJSON(
      data.presentation_proposal["request_presentations~attach"].data,
      ProofRequest
    );

    // TODO: AFJ doesn't support to negotiate proposal yet
    // if thread id is present
    const proofRecord = await this.agent.proof.requestProof(
      data.connection_id,
      {
        requestedAttributes: proofRequest.requestedAttributes,
        requestedPredicates: proofRequest.requestedPredicates,
      },
      {
        comment: data.presentation_proposal.comment,
      }
    );

    return this.mapProofRecord(proofRecord);
  }

  @Post("/send-presentation")
  async sendPresentation(
    @BodyParams("id") threadId: string,
    @BodyParams("data") data: any
  ) {
    let proofRecord = await this.agent.proof.getByThreadId(threadId);

    const requestedCredentials = JsonTransformer.fromJSON(
      {
        requested_attributes: data.requested_attributes ?? new Map(),
        requested_predicates: data.requested_predicates ?? new Map(),
        self_attested_attributes: data.self_attested_attributes ?? new Map(),
      },
      RequestedCredentials
    );

    console.log(requestedCredentials);

    proofRecord = await this.agent.proof.acceptRequest(
      proofRecord.id,
      requestedCredentials
    );

    return this.mapProofRecord(proofRecord);
  }

  @Post("/verify-presentation")
  async verifyPresentation(@BodyParams("id") threadId: string) {
    let proofRecord = await this.agent.proof.getByThreadId(threadId);

    proofRecord = await this.agent.proof.acceptPresentation(proofRecord.id);

    return this.mapProofRecord(proofRecord);
  }

  private mapProofRecord(proofRecord: ProofRecord) {
    return {
      state: proofRecord.state.toLowerCase().replace("_", "-"),
      thread_id: proofRecord.tags.threadId,
    };
  }
}
