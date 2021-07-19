import { Controller, Get, PathParams, Post, BodyParams } from "@tsed/common";
import { NotFound } from "@tsed/exceptions";
import {
  Agent,
  JsonTransformer,
  PresentationPreview,
  ProofRequest,
  RequestedCredentials,
  ProofRecord,
  RequestedAttribute,
  IndyCredentialInfo,
} from "aries-framework";
import { request } from "express";
import { CredentialUtils } from "../utils/CredentialUtils";
import { ProofUtils } from "../utils/ProofUtils";

@Controller("/agent/command/proof")
export class PresentProofController {
  private agent: Agent;
  private proofUtils: ProofUtils;

  public constructor(agent: Agent) {
    this.agent = agent;
    this.proofUtils = new ProofUtils(agent);
  }

  @Get("/:threadId")
  async getProofByThreadId(@PathParams("threadId") threadId: string) {
    const proofRecord = await this.proofUtils.getProofByThreadId(threadId);

    if (!proofRecord) {
      throw new NotFound(`proof record for thead id "${threadId}" not found.`);
    }

    return this.mapProofRecord(proofRecord);
  }

  @Get("/")
  async getAllProofs() {
    const proofs = await this.agent.proofs.getAll();

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

    const proofRecord = await this.agent.proofs.proposeProof(
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
    const proofRecord = await this.agent.proofs.requestProof(
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
    @BodyParams("data")
    data: {
      self_attested_attributes: Record<string, string>;
      requested_attributes: Record<
        string,
        { cred_id: string; timestamp?: number; revealed: boolean }
      >;
      requested_predicates: Record<
        string,
        { cred_id: string; revealed: boolean }
      >;
      comment: string;
    }
  ) {
    let proofRecord = await this.proofUtils.getProofByThreadId(threadId);

    if (proofRecord) {
      const requestedCredentials = JsonTransformer.fromJSON(
        {
          requested_attributes: data.requested_attributes ?? new Map(),
          requested_predicates: data.requested_predicates ?? new Map(),
          self_attested_attributes: data.self_attested_attributes ?? new Map(),
        },
        RequestedCredentials
      );

      const credentialUtils = new CredentialUtils(this.agent);
      Object.values(requestedCredentials.requestedAttributes).forEach(
        async (requestedAttribute) => {
          const credentialInfo = JsonTransformer.fromJSON(
            await credentialUtils.getCredentialByThreadId(
              requestedAttribute.credentialId
            ),
            IndyCredentialInfo
          );
          requestedAttribute.credentialInfo = credentialInfo;
        }
      );

      proofRecord = await this.agent.proofs.acceptRequest(
        proofRecord.id,
        requestedCredentials,
        { comment: data.comment }
      );

      return this.mapProofRecord(proofRecord);
    }
  }

  @Post("/verify-presentation")
  async verifyPresentation(@BodyParams("id") threadId: string) {
    let proofRecord = await this.proofUtils.getProofByThreadId(threadId);
    if (proofRecord) {
      return this.mapProofRecord(
        await this.agent.proofs.acceptPresentation(proofRecord.id)
      );
    }
  }

  private mapProofRecord(proofRecord: ProofRecord) {
    return {
      state: proofRecord.state.toLowerCase(),
      thread_id: proofRecord.threadId,
    };
  }
}
