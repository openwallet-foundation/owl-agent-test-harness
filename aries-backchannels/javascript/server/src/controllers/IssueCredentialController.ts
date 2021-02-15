import { Controller, Get, PathParams, Post, BodyParams } from "@tsed/common";
import { BadRequest, NotFound } from "@tsed/exceptions";
import {
  Agent,
  JsonTransformer,
  CredentialRecord,
  CredentialPreview,
} from "aries-framework-javascript";

@Controller("/agent/command/issue-credential")
export class IssueCredentialController {
  private agent: Agent;

  public constructor(agent: Agent) {
    this.agent = agent;
  }

  @Get("/:threadId")
  async getCredentialByThreadId(@PathParams("threadId") threadId: string) {
    const credential = await this.agent.credentials.getByThreadId(threadId);

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

    if (threadId) {
      const credential = await this.agent.credentials.getByThreadId(threadId);

      credentialRecord = await this.agent.credentials.acceptProposal(
        credential.id
      );
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
    } else {
      throw new BadRequest(`Missing both id and data properties`);
    }

    return this.mapCredential(credentialRecord);
  }

  @Post("/send-request")
  async sendRequest(@BodyParams("id") threadId: string) {
    let credentialRecord = await this.agent.credentials.getByThreadId(threadId);

    credentialRecord = await this.agent.credentials.acceptOffer(
      credentialRecord.id
    );

    return this.mapCredential(credentialRecord);
  }

  @Post("/issue")
  async acceptRequest(
    @BodyParams("id") threadId: string,
    // TODO: add credential_preview
    @BodyParams("data") data?: { comment?: string }
  ) {
    let credentialRecord = await this.agent.credentials.getByThreadId(threadId);

    credentialRecord = await this.agent.credentials.acceptRequest(
      credentialRecord.id
    );

    return this.mapCredential(credentialRecord);
  }

  @Post("/store")
  async storeCredential(
    @BodyParams("id") threadId: string,
    @BodyParams("data") data: any
  ) {
    let credentialRecord = await this.agent.credentials.getByThreadId(threadId);

    credentialRecord = await this.agent.credentials.acceptCredential(
      credentialRecord.id
    );

    return this.mapCredential(credentialRecord);
  }

  private mapCredential(credential: CredentialRecord) {
    return {
      state: credential.state.toLowerCase().replace("_", "-"),
      credential_id: credential.credentialId,
      thread_id: credential.tags.threadId,
    };
  }
}
