# Project closure review — Cyber Risk & IAM Decision Study

**Version:** v1.0 educational case study  
**Closure date:** 3 November 2026  
**Status:** COMPLETE within its expressly limited fictional/synthetic portfolio scope  
**Owner:** Federica Iengo  
**Evidence:** [GitHub Actions run 41565390636](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/41565390636) — source commit `a99eb36261dea42dcf38251e62f85724a4682608`, **COMPLETED / SUCCESS**.

## Scope and acceptance criteria

| Acceptance criterion | Actual evidence | Closure |
| --- | --- | --- |
| A bounded risk register with transparent assumptions | `risk_register.json`: 12 invented assets and 12 hypothetical risks; proposal-only controls | PASS |
| A vendor-evidence request instrument | `vendor_due_diligence.json`: 12 questions; none represented as answered | PASS |
| A synthetic identity and access-decision exercise | 20 fictional identities; 24 scenario fixtures; `04_EVALUATE_ACCESS.py` output reviewed by CI | PASS |
| A document/tenant/approval-scoped negative-testing exercise | `05_DOCUMENT_SCOPE_POLICY.py` plus `test_document_scope.py` | PASS |
| Reproducible automated validation with a current execution | [CI run 41565390636](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/41565390636): Python 3.13 syntax check, risk validator, full unittest suite, 24-case IAM script, all workflow steps SUCCESS | PASS |
| Stakeholder-facing decision and explicitly limited outcome | `DECISION_BRIEF.md`: fictional supplier decision **HOLD**, missing evidence, residual risk **NOT ASSESSED** | PASS |
| Guard against false security/experience claims | Scope, source fixtures and limitations disclosed in `README.md` and this review | PASS |

## Regression accounting

The current repository contains **58 Python unittest methods**, divided into:

- `test_risks.py`: **11** risk and vendor checklist methods.
- `test_iam_access.py`: **16** synthetic IAM policy methods, including a method exercising **24 scenario fixtures**.
- `test_document_scope.py`: **31** document/tenant/approval-scope methods.

The automated workflow runs these three test modules as one suite. The suite step, Python syntax check, risk validator and separate 24-scenario IAM CLI step all completed successfully in the cited run. **58 refers to test methods, not 58 different security controls or tests of real infrastructure.** The 51/51 figure in earlier notes is a historical snapshot and has been superseded by the current full-suite check.

## Decision to close v1.0

The portfolio case study has a complete, reviewable educational deliverable: synthetic inputs, executable evaluators, a traceable decision brief, negative cases, and a verified regression gate that reruns automatically when this folder or its workflow changes.

**Closure does not mean** that a real vendor was vetted, that access controls were deployed, that tenant isolation or security standards were independently certified, or that a penetration test or compliance audit was conducted. The simulated approval registry is not a trusted authority and must not be used for real authorization decisions. Residual risk for any real organization remains **NOT ASSESSED**.

No outstanding item blocks **this educational portfolio v1.0**. Any expansion to a real security assurance process, a new threat model, a different application, external review, or live deployment must be scoped and authorized as a *new* engagement or version. The existing code and decision brief are retained as an auditable reference, with CI continuing to run on future source changes.
