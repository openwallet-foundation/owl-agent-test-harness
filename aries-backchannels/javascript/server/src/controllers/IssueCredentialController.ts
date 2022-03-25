import { BodyParams, Controller, Get, PathParams, Post } from '@tsed/common'
import { BadRequest, NotFound } from '@tsed/exceptions'
import {
  CredentialEventTypes,
  CredentialPreview,
  CredentialRecord,
  CredentialState,
  CredentialStateChangedEvent,
  JsonTransformer,
} from '@aries-framework/core'
import { CredentialUtils } from '../utils/CredentialUtils'
import { filter, firstValueFrom, ReplaySubject, timeout } from 'rxjs'
import { BaseController } from '../BaseController'
import { TestHarnessConfig } from '../TestHarnessConfig'

@Controller('/agent/command/issue-credential')
export class IssueCredentialController extends BaseController {
  private subject = new ReplaySubject<CredentialStateChangedEvent>()

  public constructor(testHarnessConfig: TestHarnessConfig) {
    super(testHarnessConfig)
  }

  public onStartup() {
    this.subject = new ReplaySubject<CredentialStateChangedEvent>()
    // Catch all events in replay subject for later use
    this.agent.events
      .observable<CredentialStateChangedEvent>(CredentialEventTypes.CredentialStateChanged)
      .subscribe(this.subject)
  }

  @Get('/:threadId')
  async getCredentialByThreadId(@PathParams('threadId') threadId: string) {
    const credential = await CredentialUtils.getCredentialByThreadId(this.agent, threadId)
    if (!credential) {
      throw new NotFound(`credential for thead id "${threadId}" not found.`)
    }
    return this.mapCredential(credential)
  }

  @Get('/')
  async getAllCredentials() {
    const credentials = await this.agent.credentials.getAll()

    return credentials.map((cred) => this.mapCredential(cred))
  }

  @Post('/send-proposal')
  async sendProposal(
    @BodyParams('data')
    data: {
      connection_id: string
      schema_issuer_did?: string
      issuer_did?: string
      schema_name?: string
      cred_def_id?: string
      schema_version?: string
      schema_id?: string
      credential_proposal: any
    }
  ) {
    const credentialRecord = await this.agent.credentials.proposeCredential(data.connection_id, {
      schemaIssuerDid: data.schema_issuer_did,
      issuerDid: data.issuer_did,
      schemaName: data.schema_name,
      credentialDefinitionId: data.cred_def_id,
      schemaVersion: data.schema_version,
      schemaId: data.schema_id,
      credentialProposal: JsonTransformer.fromJSON(data.credential_proposal, CredentialPreview),
    })

    return this.mapCredential(credentialRecord)
  }

  @Post('/send-offer')
  async sendOffer(
    @BodyParams('id') threadId?: string,
    @BodyParams('data')
    data?: {
      connection_id: string
      cred_def_id: string
      credential_preview: any
    }
  ) {
    let credentialRecord: CredentialRecord

    if (threadId) {
      await this.waitForState(threadId, CredentialState.ProposalReceived)
      const { id } = await CredentialUtils.getCredentialByThreadId(this.agent, threadId)
      credentialRecord = await this.agent.credentials.acceptProposal(id)
      return this.mapCredential(credentialRecord)
    } else if (data) {
      credentialRecord = await this.agent.credentials.offerCredential(data.connection_id, {
        credentialDefinitionId: data.cred_def_id,
        preview: JsonTransformer.fromJSON(data.credential_preview, CredentialPreview),
      })
      return this.mapCredential(credentialRecord)
    } else {
      throw new BadRequest(`Missing both id and data properties`)
    }
  }

  @Post('/send-request')
  async sendRequest(@BodyParams('id') threadId: string) {
    await this.waitForState(threadId, CredentialState.OfferReceived)
    let { id } = await CredentialUtils.getCredentialByThreadId(this.agent, threadId)

    const credentialRecord = await this.agent.credentials.acceptOffer(id)
    return this.mapCredential(credentialRecord)
  }

  @Post('/issue')
  async acceptRequest(@BodyParams('id') threadId: string, @BodyParams('data') data?: { comment?: string }) {
    await this.waitForState(threadId, CredentialState.RequestReceived)
    const { id } = await CredentialUtils.getCredentialByThreadId(this.agent, threadId)

    const credentialRecord = await this.agent.credentials.acceptRequest(id, {
      comment: data?.comment,
    })
    return this.mapCredential(credentialRecord)
  }

  @Post('/store')
  async storeCredential(@BodyParams('id') threadId: string) {
    await this.waitForState(threadId, CredentialState.CredentialReceived)
    let { id } = await CredentialUtils.getCredentialByThreadId(this.agent, threadId)
    const credentialRecord = await this.agent.credentials.acceptCredential(id)

    return this.mapCredential(credentialRecord)
  }

  private async waitForState(threadId: string, state: CredentialState) {
    return await firstValueFrom(
      this.subject.pipe(
        filter((c) => c.payload.credentialRecord.threadId === threadId),
        filter((c) => c.payload.credentialRecord.state === state),
        timeout(20000)
      )
    )
  }

  private mapCredential(credentialRecord: CredentialRecord) {
    return {
      state: credentialRecord.state,
      credential_id: credentialRecord.credentialId,
      thread_id: credentialRecord.threadId,
    }
  }
}
