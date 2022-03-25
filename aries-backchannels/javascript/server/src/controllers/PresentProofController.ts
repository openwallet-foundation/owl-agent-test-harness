import { Controller, Get, PathParams, Post, BodyParams } from '@tsed/common'
import { NotFound } from '@tsed/exceptions'
import {
  JsonTransformer,
  PresentationPreview,
  ProofRequest,
  RequestedCredentials,
  ProofRecord,
  AgentConfig,
  Logger,
  ProofEventTypes,
  ProofStateChangedEvent,
  ProofState,
  RequestedAttribute,
  RequestedPredicate,
} from '@aries-framework/core'
import { ProofUtils } from '../utils/ProofUtils'
import { filter, firstValueFrom, ReplaySubject, timeout } from 'rxjs'
import util from 'util'
import { BaseController } from '../BaseController'
import { TestHarnessConfig } from '../TestHarnessConfig'

@Controller('/agent/command/proof')
export class PresentProofController extends BaseController {
  private logger: Logger
  private subject = new ReplaySubject<ProofStateChangedEvent>()

  public constructor(testHarnessConfig: TestHarnessConfig) {
    super(testHarnessConfig)

    this.logger = this.agent.injectionContainer.resolve(AgentConfig).logger
  }

  public onStartup() {
    this.subject = new ReplaySubject<ProofStateChangedEvent>()
    // Catch all events in replay subject for later use
    this.agent.events.observable<ProofStateChangedEvent>(ProofEventTypes.ProofStateChanged).subscribe(this.subject)
  }

  @Get('/:threadId')
  async getProofByThreadId(@PathParams('threadId') threadId: string) {
    const proofRecord = await ProofUtils.getProofByThreadId(this.agent, threadId)

    if (!proofRecord) {
      throw new NotFound(`proof record for thead id "${threadId}" not found.`)
    }

    return this.mapProofRecord(proofRecord)
  }

  @Get('/')
  async getAllProofs() {
    const proofs = await this.agent.proofs.getAll()

    return proofs.map((proof) => this.mapProofRecord(proof))
  }

  @Post('/send-proposal')
  async sendProposal(
    @BodyParams('data')
    data: {
      connection_id: string
      presentation_proposal: {
        comment?: string
        attributes: any
        predicates: any
      }
    }
  ) {
    const { attributes, predicates, ...restProposal } = data.presentation_proposal

    const newPresentationProposal = {
      ...restProposal,
      attributes: attributes,
      predicates: predicates,
    }
    const presentationProposal = JsonTransformer.fromJSON(newPresentationProposal, PresentationPreview)

    const proofRecord = await this.agent.proofs.proposeProof(data.connection_id, presentationProposal, {
      comment: data.presentation_proposal.comment,
    })

    return this.mapProofRecord(proofRecord)
  }

  @Post('/send-request')
  async sendRequest(
    @BodyParams('id') threadId: string,
    @BodyParams('data')
    data: {
      connection_id: string
      presentation_request: {
        comment?: string
        proof_request: {
          data: unknown
        }
      }
    }
  ) {
    const proofRequest = JsonTransformer.fromJSON(data.presentation_request.proof_request.data, ProofRequest)

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
    )

    return this.mapProofRecord(proofRecord)
  }

  @Post('/send-presentation')
  async sendPresentation(
    @BodyParams('id') threadId: string,
    @BodyParams('data')
    data: {
      self_attested_attributes: Record<string, string>
      requested_attributes: Record<string, { cred_id: string; timestamp?: number; revealed: boolean }>
      requested_predicates: Record<string, { cred_id: string; revealed: boolean }>
      comment: string
    }
  ) {
    await this.waitForState(threadId, ProofState.RequestReceived)
    let proofRecord = await ProofUtils.getProofByThreadId(this.agent, threadId)

    const requestedCredentials = JsonTransformer.fromJSON(
      {
        requested_attributes: data.requested_attributes ?? {},
        requested_predicates: data.requested_predicates ?? {},
        self_attested_attributes: data.self_attested_attributes ?? {},
      },
      RequestedCredentials
    )

    const retrievedCredentials = await this.agent.proofs.getRequestedCredentialsForProofRequest(proofRecord.id, {
      filterByPresentationPreview: true,
      // Some tests include presenting a revoked credential, expecting the verification to fail
      // So not excluding those from the retrieved credentials.
      filterByNonRevocationRequirements: false,
    })

    this.logger.info('Created proof request', {
      requestedCredentials: util.inspect(requestedCredentials, { showHidden: false, depth: null }),
      retrievedCredentials: util.inspect(retrievedCredentials, { showHidden: false, depth: null }),
    })

    Object.keys(requestedCredentials.requestedAttributes).forEach((key) => {
      requestedCredentials.requestedAttributes[key] = retrievedCredentials.requestedAttributes[key].find(
        (a) => a.credentialId === requestedCredentials.requestedAttributes[key].credentialId
      ) as RequestedAttribute
    })

    Object.keys(requestedCredentials.requestedPredicates).forEach((key) => {
      requestedCredentials.requestedPredicates[key] = retrievedCredentials.requestedPredicates[key].find(
        (p) => p.credentialId === requestedCredentials.requestedPredicates[key].credentialId
      ) as RequestedPredicate
    })

    proofRecord = await this.agent.proofs.acceptRequest(proofRecord.id, requestedCredentials, {
      comment: data.comment,
    })

    return this.mapProofRecord(proofRecord)
  }

  @Post('/verify-presentation')
  async verifyPresentation(@BodyParams('id') threadId: string) {
    await this.waitForState(threadId, ProofState.PresentationReceived)

    let proofRecord = await ProofUtils.getProofByThreadId(this.agent, threadId)
    if (proofRecord) {
      return this.mapProofRecord(await this.agent.proofs.acceptPresentation(proofRecord.id))
    }
  }

  private async waitForState(threadId: string, state: ProofState) {
    return await firstValueFrom(
      this.subject.pipe(
        filter((c) => c.payload.proofRecord.threadId === threadId),
        filter((c) => c.payload.proofRecord.state === state),
        timeout(20000)
      )
    )
  }

  private mapProofRecord(proofRecord: ProofRecord) {
    return {
      state: proofRecord.state,
      thread_id: proofRecord.threadId,
    }
  }
}
