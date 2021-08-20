import { Controller, Get, PathParams, Post, BodyParams } from "@tsed/common";
import { NotFound } from "@tsed/exceptions";
import {
  Agent,
  JsonTransformer,
  PresentationPreview,
  ProofRequest,
  RequestedCredentials,
  ProofRecord,
  IndyCredentialInfo,
  AgentConfig,
  Logger,
} from "@aries-framework/core";
import { CredentialUtils } from "../utils/CredentialUtils";
import { ProofUtils } from "../utils/ProofUtils";

@Controller("/agent/command/proof")
export class PresentProofController {
  private agent: Agent;
  private logger: Logger;
  private proofUtils: ProofUtils;

  public constructor(agent: Agent) {
    this.agent = agent;
    this.logger = agent.injectionContainer.resolve(AgentConfig).logger;
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
      presentation_proposal: {
        comment?: string;
        attributes: any;
        predicates: any;
      };
    }
  ) {
    const { attributes, predicates, ...restProposal } =
      data.presentation_proposal;

    const newPresentationProposal = {
      ...restProposal,
      attributes: attributes,
      predicates: predicates,
    };
    const presentationProposal = JsonTransformer.fromJSON(
      newPresentationProposal,
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
      presentation_request: any;
    }
  ) {
    const proofRequest = JsonTransformer.fromJSON(
      data.presentation_request["proof_request"].data,
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
        comment: data.presentation_request.comment,
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

    const requestedCredentials = JsonTransformer.fromJSON(
      {
        requested_attributes: data.requested_attributes ?? {},
        requested_predicates: data.requested_predicates ?? {},
        self_attested_attributes: data.self_attested_attributes ?? {},
      },
      RequestedCredentials
    );

    this.logger.info("Created requested credentials ", {
      requestedCredentials: JSON.stringify(
        requestedCredentials.toJSON(),
        null,
        2
      ),
    });

    const credentialUtils = new CredentialUtils(this.agent);
    Object.values(requestedCredentials.requestedAttributes).forEach(
      async (requestedAttribute) => {
        const credentialInfo = JsonTransformer.fromJSON(
          await credentialUtils.getIndyCredentialById(
            requestedAttribute.credentialId
          ),
          IndyCredentialInfo
        );
        requestedAttribute.credentialInfo = credentialInfo;
      }
    );
    Object.values(requestedCredentials.requestedPredicates).forEach(
      async (requestedPredicate) => {
        const credentialInfo = JsonTransformer.fromJSON(
          await credentialUtils.getIndyCredentialById(
            requestedPredicate.credentialId
          ),
          IndyCredentialInfo
        );
        requestedPredicate.credentialInfo = credentialInfo;
      }
    );

    this.logger.info("Created proof request ", {
      requestedCredentials: requestedCredentials.toJSON(),
    });

    proofRecord = await this.agent.proofs.acceptRequest(
      proofRecord.id,
      requestedCredentials,
      { comment: data.comment }
    );

    return this.mapProofRecord(proofRecord);
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
      state: proofRecord.state,
      thread_id: proofRecord.threadId,
    };
  }
}
