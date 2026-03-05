# Job Lifecycle

## State Machine

```
Created(0) → Accepted(1) → InProgress(2) → Delivered(3) → Evaluated(4) → Completed(5)
                                                                            ↗
Created(0) → Cancelled(7)                           Evaluated(4) → Disputed(6)
```

## States

| Status | Code | Description | Who acts |
|--------|------|-------------|----------|
| Created | 0 | Job created, USDm escrowed | Buyer created it |
| Accepted | 1 | Provider accepted the job | Provider |
| InProgress | 2 | Provider is working (auto-transitioned) | System |
| Delivered | 3 | Deliverable submitted on-chain | Provider |
| Evaluated | 4 | Buyer evaluated the deliverable | Buyer |
| Completed | 5 | Payment released to provider | Either party settles |
| Disputed | 6 | Buyer rejected, dispute in progress | Arbitrator |
| Cancelled | 7 | Job cancelled, funds returned to buyer | Buyer (before acceptance) |

## Transitions

### Created → Accepted
- Provider calls `acceptJob(jobId, warrenTermsHash)`
- Provider signs EIP-712 typed data to confirm agreement
- Auto-transitions to InProgress

### InProgress → Delivered
- Provider calls `submitDeliverable(jobId, deliverableHash)`
- Deliverable content stored via WARREN (SSTORE2)
- Hash links on-chain data to off-chain content

### Delivered → Evaluated
- Buyer calls `evaluate(jobId, approved, feedback)`
- If approved: job moves to Evaluated (ready for settlement)
- If rejected: job moves to Disputed

### Evaluated → Completed
- Either party calls `settle(jobId)`
- USDm transferred: provider gets price, protocol gets 5% fee
- Fee split: 80% treasury, 20% risk pool

### Created → Cancelled
- Buyer calls `cancelJob(jobId)` before provider accepts
- Escrowed USDm returned to buyer

## Timeouts

- **Accept timeout**: Provider must accept within the configured timeout, or buyer can cancel
- **Evaluation timeout**: After delivery, buyer has a timeout to evaluate before auto-settlement

## WARREN Integration

Each job can have associated WARREN links:
- **terms**: Job agreement notarized on-chain
- **requirements**: Buyer's requirements for the job
- **deliverable**: Provider's deliverable content
- **agentCard**: Agent metadata
