# The access decision: what would justify a limited vendor pilot?

**Independent educational business brief | October 2026 | Entirely fictional scenario**

**Decision: HOLD.** A simulated document-processing supplier has a plausible business purpose, but no evidence has been obtained to establish that access to customer files would be sufficiently restricted, monitored and revocable.

This is a decision-making exercise using invented identities, vendor questions, approvals and risks. It is **not** a real due-diligence exercise, customer engagement, implemented control, audit or recommendation to deploy.

## The business question

A B2B SaaS business is considering an external document-processing integration. Before approving access, the relevant question is not just whether the supplier can authenticate. It is:

> Can the company establish, using independently reviewed evidence, that this supplier should access these specific documents, for this purpose, during this period?

The underlying exercise documents 12 hypothetical risks, 12 draft vendor-assurance questions, 20 invented identities and 24 access-decision scenarios. The local risk rankings are illustrative; no actual likelihoods or residual-risk levels have been measured.

## A practical decision checklist

| Decision gate | What needs to be established | Example evidence to ask for | Decision if missing |
| --- | --- | --- | --- |
| Purpose and data scope | Why processing is necessary, which data categories may leave the system, and who owns the decision | Approved data flow, document classifications and data-owner sign-off | HOLD |
| Identity and least privilege | Access is limited to specific tenants, documents, actions and expiry dates | Reviewed effective permissions, approval records and negative access tests | HOLD |
| Supplier and subprocessors | Which entities will process data, where, and on what terms | Current supplier/subprocessor list and appropriate legal/privacy review | HOLD |
| Detection and response | Unexpected access can be identified, investigated and stopped | Event logs, escalation contacts, revocation exercise and response procedures | HOLD |
| Data lifecycle and recovery | Data can be retained, deleted and recovered within agreed boundaries | Retention schedule, deletion verification and restoration exercise | HOLD |
| Accountability | Someone authorized can challenge evidence and accept any remaining risk | Named risk owner, independent review, scoped decision record and expiry | HOLD |

These are **proposed questions**, not proof that an organization is compliant or that any safeguard is operating. No requests have been sent to a real supplier; no documents or tests from a real system have been assessed.

## What could change the answer?

A limited pilot could be *considered* only after the right owners verify the access purpose, restrict the data scope, review the evidence and formally document a decision. Unresolved high-impact issues might still justify rejection. A completed checklist by itself cannot approve a vendor.

The outcomes in this **fictional** model are:

- **HOLD:** key evidence is missing or contradictory. This is the current simulated state.
- **REJECT:** a disqualifying condition is established.
- **CONSIDER A LIMITED PILOT:** accountable owners have assessed evidence, boundaries, monitoring, revocation and remaining risk. This exercise has **not** reached that state.

**Residual risk: NOT ASSESSED.** Assigning a favorable residual score without checking the safeguards would disguise uncertainty as confidence.

## One flaw discovered during review

An early toy access evaluator allowed any nonempty approval identifier to satisfy an approval check. This was not adequate: an identifier could be unrelated to the requester or document.

The revised **simulated** evaluator binds sample approvals to a specific subject, tenant, document, action, purpose and expiry, with negative regression cases. This is a lesson in validating assumptions, **not** evidence that a real identity provider, tenant boundary or approval service has been secured.

## What a recruiter can inspect

The accompanying [synthetic case-study data, Python examples and tests](./README.md) are published for reproducibility. The reported 51 passing Python unittest methods test internal rules on fictional inputs. They do not prove production safety, compliance, an independent audit or real-world incident reduction.

**Transferable work illustrated:** clarifying a decision, requesting appropriate evidence, identifying unsupported claims, documenting exceptions, tracing assumptions and explaining the outcome to stakeholders.

**Not claimed:** professional cybersecurity employment, an actual vendor assessment, authority to approve access or implementation of live security controls.
