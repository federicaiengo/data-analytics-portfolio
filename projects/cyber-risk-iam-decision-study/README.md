# A Valid Login Is Not a Trust Decision

**Independent educational case study · Cybersecurity GRC · IT Risk · IAM governance · Python**

A fictional B2B SaaS company wants a supplier to process a limited set of customer documents. **What evidence would justify access to one specified record, for one tenant, for one purpose—and when should the decision remain on hold?**

All suppliers, documents, principals, approvals, evidence assumptions and risk ratings here are **synthetic**. No client work, live systems, genuine vendor assessment, penetration testing or operational controls are claimed.

**Prefer the business decision to the code?** [Start with the plain-English vendor decision brief](DECISION_BRIEF.md). It explains why the fictional recommendation remains HOLD, what evidence would be needed, and who would be responsible for deciding. No real supplier was assessed.

## What I built

- A structured register of **12 hypothetical risks**, with explicit ordinal likelihood/impact assumptions and candidate controls.
- A **12-question vendor due-diligence checklist**, with unanswered evidence requests.
- Five fictional IAM roles, **20 synthetic identities**, and **24 access-decision fixtures**.
- Small Python examples to reason about identity status, least privilege, tenant scope, individual document approval, purpose and expiry.
- Tests for unsafe assumptions, including expired access, access across tenants, self-approval and reuse of an approval belonging to a different user or document.

The exercise uncovered a weakness in an initial toy model: a nonempty approval identifier was insufficient. I replaced it with a **simulated** binding to principal, tenant, document, purpose, operation and expiration, and added negative regression tests. The registry is not a real trusted approval authority.

## Reproducibility

From this folder with Python 3.13 or a compatible Python 3 version:

```bash
python -m unittest -v test_risks.py test_iam_access.py test_document_scope.py
python validate_risks.py
```

The 2026-10-14 review recorded **51 of 51 Python unittest methods passing**: 11 for risk and vendor fixture consistency, 16 for IAM decision logic (including 24 scenario subcases), and 24 for document/tenant decisions. These results were reproduced on the published synthetic source snapshots before publication.

**Important:** passing tests validate toy-model logic, *not the security of a real system, real-world tenant isolation, cryptographic identity, evidence provenance or policy enforcement*. No automated test can establish that an imaginary supplier is safe.

## Later regression review (18 October 2026)

A second review of the **fictional document-scope evaluator** found a genuine testable flaw: treating expiration dates as unchecked strings could grant simulated access when dates were malformed, and some invalid values raised exceptions rather than returning DENY. Earlier negative tests also exposed ambiguity from duplicated identity records and malformed approval identifiers.

The toy evaluator now fails closed for invalid or noncanonical calendar dates, duplicated subject records and malformed approval input. The [document-scope test module](test_document_scope.py) passed **31/31 Python unittest methods locally**, using source files verified byte for byte against their committed Git blobs. These are software regression results on fabricated examples, **not evidence of real access-control enforcement**. The 51/51 figure above remains the historical 14 October full-project snapshot; the entire project suite has **not yet been rerun** since these improvements.

## Decision memorandum

The fictional vendor's status is **HOLD**: permissions, retention/deletion, subcontractors, logging, incident response, and evidence of control operation would need to be independently assessed before any actual business decision. **Residual risk: NOT ASSESSED.** The risk register's 1–5 ordinal scores and multiplication are illustrative local ranking choices; they are not measured incident probabilities or a NIST-specified formula.

## Contents

| Files | Purpose |
|---|---|
| `risk_register.json`, `vendor_due_diligence.json` | Invented risk inventory and unrequested vendor evidence |
| `validate_risks.py`, `test_risks.py` | Risk schema/consistency checks |
| `04_IDENTITY_FIXTURES.json`, `04_ACCESS_SCENARIOS.json` | Fake identities and access requests |
| `04_EVALUATE_ACCESS.py`, `test_iam_access.py` | Simplified IAM decision simulator and tests |
| `05_DOCUMENT_SCOPE_POLICY.py`, `test_document_scope.py` | Illustrative document-scoped access and negative tests |

## What this project does *not* prove

No real employer, supplier, customer, identity provider, audit, breach reduction, compliance outcome, certification, external security review or verified production access-control system is represented. The evaluator accepts hypothetical assurance assertions from its caller and must **never** be deployed to authorize access.

The underlying approach draws on NIST CSF 2.0, NIST SP 800-30 Rev. 1 and NIST SP 800-207, without implying conformity or certification:

- [NIST CSF 2.0](https://www.nist.gov/cyberframework)
- [NIST SP 800-30 Rev. 1](https://csrc.nist.gov/pubs/sp/800/30/r1/final)
- [NIST SP 800-207](https://www.nist.gov/publications/zero-trust-architecture)

**Portfolio interpretation:** this is evidence of analytical reasoning, scoped programming practice, data validation and a willingness to challenge assumptions—not a substitute for professional cybersecurity experience.
