import { BodyParams, Controller, Get, PathParams, Post } from "@tsed/common";
import { BadRequest, NotFound } from "@tsed/exceptions";
import {
  Agent,
  CredentialPreview,
  CredentialRecord,
  JsonTransformer,
} from "@aries-framework/core";
import { CredentialUtils } from "../utils/CredentialUtils";

@Controller("/agent/command/issue-credential")
export class IssueCredentialController {
  private agent: Agent;
  private credentialUtils: CredentialUtils;

  public constructor(agent: Agent) {
    this.agent = agent;
    this.credentialUtils = new CredentialUtils(agent);
  }

  @Get("/:threadId")
  async getCredentialByThreadId(@PathParams("threadId") threadId: string) {
    const credential = await this.credentialUtils.getCredentialByThreadId(
      threadId
    );
    if (!credential) {
      throw new NotFound(`credential for thead id "${threadId}" not found.`);
    }
    return this.mapCredential(credential);
  }

  @Get("/")
  async getAllConnections() {
    const credentials = await this.agent.credentials.getAll();

    return credentials.map((cred) => this.mapCredential(cred));
  }

  @Post("/send-proposal")
  async sendProposal(
    @BodyParams("data")
    data: {
      connection_id: string;
      schema_issuer_did?: string;
      issuer_did?: string;
      schema_name?: string;
      cred_def_id?: string;
      schema_version?: string;
      schema_id?: string;
      credential_proposal: any;
    }
  ) {
    const credentialRecord = await this.agent.credentials.proposeCredential(
      data.connection_id,
      {
        schemaIssuerDid: data.schema_issuer_did,
        issuerDid: data.issuer_did,
        schemaName: data.schema_name,
        credentialDefinitionId: data.cred_def_id,
        schemaVersion: data.schema_version,
        schemaId: data.schema_id,
        credentialProposal: JsonTransformer.fromJSON(
          data.credential_proposal,
          CredentialPreview
        ),
      }
    );

    return this.mapCredential(credentialRecord);
  }

  @Post("/send-offer")
  async sendOffer(
    @BodyParams("id") threadId?: string,
    @BodyParams("data")
    data?: {
      connection_id: string;
      cred_def_id: string;
      credential_preview: any;
    }
  ) {
    let credentialRecord: CredentialRecord;
    await new Promise(f => setTimeout(f, 10000));
    if (threadId) {
      const { id } = await this.credentialUtils.getCredentialByThreadId(
        threadId
      );
      credentialRecord = await this.agent.credentials.acceptProposal(id);
      return this.mapCredential(credentialRecord);
    } else if (data) {
      credentialRecord = await this.agent.credentials.offerCredential(
        data.connection_id,
        {
          credentialDefinitionId: data.cred_def_id,
          preview: JsonTransformer.fromJSON(
            data.credential_preview,
            CredentialPreview
          ),
        }
      );
      return this.mapCredential(credentialRecord);
    } else {
      throw new BadRequest(`Missing both id and data properties`);
    }
  }

  @Post("/send-request")
  async sendRequest(@BodyParams("id") threadId: string) {
    let { id } = await this.credentialUtils.getCredentialByThreadId(threadId);

    const credentialRecord = await this.agent.credentials.acceptOffer(id);
    return this.mapCredential(credentialRecord);
  }

  @Post("/issue")
  async acceptRequest(
    @BodyParams("id") threadId: string,
    @BodyParams("data") data?: { comment?: string }
  ) {
    const { id } = await this.credentialUtils.getCredentialByThreadId(threadId);

    const credentialRecord = await this.agent.credentials.acceptRequest(id, {
      comment: data?.comment,
    });
    return this.mapCredential(credentialRecord);
  }

  @Post("/store")
  async storeCredential(@BodyParams("id") threadId: string) {
    let { id } = await this.credentialUtils.getCredentialByThreadId(threadId);
    const credentialRecord = await this.agent.credentials.acceptCredential(id);

    return this.mapCredential(credentialRecord);
  }

  private mapCredential(credentialRecord: CredentialRecord) {
    return {
      state: credentialRecord.state,
      credential_id: credentialRecord.credentialId,
      thread_id: credentialRecord.threadId,
    };
  }
}
