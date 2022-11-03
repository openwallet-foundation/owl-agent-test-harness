import { Controller, Get, PathParams, Post, BodyParams } from '@tsed/common'
import { NotFound } from '@tsed/exceptions'
import {
  JsonTransformer,
  ProofRequest,
  ProofExchangeRecord,
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
import { ConnectionUtils } from '../utils/ConnectionUtils'
import { PresentationPreview } from '@aries-framework/core'
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

    return this.mapProofExchangeRecord(proofRecord)
  }

  @Get('/')
  async getAllProofs() {
    const proofs = await this.agent.proofs.getAll()

    return proofs.map((proof) => this.mapProofExchangeRecord(proof))
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

    const presentationProposal = JsonTransformer.fromJSON(data.presentation_proposal, PresentationPreview)
    const { attributes, predicates } = presentationProposal

    const connection = await ConnectionUtils.getConnectionByConnectionIdOrOutOfBandId(this.agent, data.connection_id)

    const proofRecord = await this.agent.proofs.proposeProof({
      connectionId: connection.id, 
      protocolVersion: 'v1',
      proofFormats: {
        indy: {
          attributes,
          predicates,
        },
      },
      comment: data.presentation_proposal.comment
    })

    return this.mapProofExchangeRecord(proofRecord)
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
    // Do not validate, we only need a few properties from the proof request
    const proofRequest = JsonTransformer.fromJSON(data.presentation_request.proof_request.data, ProofRequest, {
      validate: false,
    })

    const connection = await ConnectionUtils.getConnectionByConnectionIdOrOutOfBandId(this.agent, data.connection_id)

    // TODO: AFJ doesn't support to negotiate proposal yet
    // if thread id is present
    const proofRecord = await this.agent.proofs.requestProof({
      connectionId: connection.id,
      protocolVersion: 'v1',
      proofFormats: {
        indy: {
          requestedAttributes: proofRequest.requestedAttributes,
          requestedPredicates: proofRequest.requestedPredicates,  
        }
      },
      comment: data.presentation_request.comment,
    })

    return this.mapProofExchangeRecord(proofRecord)
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

    const retrievedCredentials = await this.agent.proofs.getRequestedCredentialsForProofRequest({
      proofRecordId: proofRecord.id, 
      config: {
      filterByPresentationPreview: true,
      // Some tests include presenting a revoked credential, expecting the verification to fail
      // So not excluding those from the retrieved credentials.
      filterByNonRevocationRequirements: false,
    }})

    let requestedAttributes: Record<string, RequestedAttribute> = {}
    let requestedPredicates: Record<string, RequestedPredicate> = {}
    
    if (data.requested_attributes) {
      Object.keys(data.requested_attributes).forEach((key) => {
        requestedAttributes[key] = retrievedCredentials.proofFormats.indy?.requestedAttributes[key]?.find(
          (a) => a.credentialId === data.requested_attributes[key].cred_id
        ) as RequestedAttribute
      })
    }
    if (data.requested_predicates) {
      Object.keys(data.requested_predicates).forEach((key) => {
        requestedPredicates[key]  = retrievedCredentials.proofFormats.indy?.requestedPredicates[key].find(
          (p) => p.credentialId ===  data.requested_predicates[key].cred_id
        ) as RequestedPredicate
      })
    }

    this.logger.info('Created proof request', {
      requestedAttributes: util.inspect(requestedAttributes, { showHidden: false, depth: null }),
      requestedPredicates: util.inspect(requestedPredicates, { showHidden: false, depth: null }),
      retrievedCredentials: util.inspect(retrievedCredentials, { showHidden: false, depth: null }),
    })

    proofRecord = await this.agent.proofs.acceptRequest({ 
      proofRecordId: proofRecord.id, 
      proofFormats: { indy: { requestedAttributes, requestedPredicates } },
      comment: data.comment,
    })

    return this.mapProofExchangeRecord(proofRecord)
  }

  @Post('/verify-presentation')
  async verifyPresentation(@BodyParams('id') threadId: string) {
    await this.waitForState(threadId, ProofState.PresentationReceived)

    let proofRecord = await ProofUtils.getProofByThreadId(this.agent, threadId)
    if (proofRecord) {
      return this.mapProofExchangeRecord(await this.agent.proofs.acceptPresentation(proofRecord.id))
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

  private mapProofExchangeRecord(proofExchangeRecord: ProofExchangeRecord) {
    return {
      state: proofExchangeRecord.state,
      thread_id: proofExchangeRecord.threadId,
    }
  }
}
