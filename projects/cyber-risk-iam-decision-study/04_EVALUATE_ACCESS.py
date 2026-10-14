"""Educational IAM policy evaluator for fictional records only. Not a production security gate."""
import json
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
PERMISSIONS = {
    "data_analyst": {("analytics_summary", "read")},
    "customer_operator": {("approved_document", "read"), ("staging_selected", "write")},
    "integration_admin": {("integration_config", "manage"), ("integration_event_logs", "read")},
    "security_reviewer": {("integration_event_logs", "read"), ("vendor_access_request", "approve")},
    "vendor_processor": {("staging_selected", "read"), ("processing_endpoint", "call")},
}
DEFAULT_FLAGS = {
    "authenticated": False, "mfa": False, "service_verified": False,
    "contract_active": False, "ticket_approved": False,
    "scope_approved": False, "source_verified": None, "requester": None,
}

def load_fixture(filename):
    return json.loads((FOLDER / filename).read_text(encoding="utf-8"))

def decide(principal, resource, action, identities, today="2026-10-14", flags=None):
    """Returns ALLOW, DENY, or ESCALATE. Escalation never grants access."""
    flags = {**DEFAULT_FLAGS, **(flags or {})}
    subject = next((item for item in identities if item["id"] == principal), None)
    if subject is None or subject["status"] != "active":
        return "DENY"
    if subject["expires_on"] <= today:
        return "DENY"
    if flags["authenticated"] is not True:
        return "DENY"
    kind = subject["kind"]
    if kind == "human" and flags["mfa"] is not True:
        return "DENY"
    if kind == "service" and flags["service_verified"] is not True:
        return "DENY"
    if (resource, action) not in PERMISSIONS.get(subject["role"], set()):
        return "DENY"
    if action == "approve" and (not flags.get("requester") or flags.get("requester") == principal):
        return "DENY"
    if resource == "staging_selected" and action == "write":
        if flags["ticket_approved"] is not True or flags["scope_approved"] is not True:
            return "DENY"
    if subject["role"] == "vendor_processor":
        if kind != "service":
            return "DENY"
        if any(flags[name] is not True for name in ("contract_active", "scope_approved", "ticket_approved")):
            return "DENY"
        if flags["source_verified"] is not True:
            return "ESCALATE"
    return "ALLOW"

def verify_fixtures(identities, cases):
    ids = [entry["id"] for entry in identities]
    case_ids = [entry["id"] for entry in cases]
    assert len(identities) == 20 and len(set(ids)) == 20
    assert len(cases) == 24 and len(set(case_ids)) == 24
    assert set(entry["role"] for entry in identities) == set(PERMISSIONS)
    assert all(entry["kind"] in ("human", "service") for entry in identities)
    assert all(case["expected"] in ("ALLOW", "DENY", "ESCALATE") for case in cases)

def review():
    i = load_fixture("04_IDENTITY_FIXTURES.json")["identities"]
    c = load_fixture("04_ACCESS_SCENARIOS.json")["cases"]
    verify_fixtures(i, c)
    results = [(case["id"], decide(case["principal"], case["resource"],
                case["action"], i, flags=case.get("flags")), case["expected"])
               for case in c]
    failures = [r for r in results if r[1] != r[2]]
    return results, failures

if __name__ == "__main__":
    outcomes, failures = review()
    for case_id, actual, expected in outcomes:
        print(f"{case_id}: {actual} / expected {expected}")
    print(f"{len(outcomes)-len(failures)}/{len(outcomes)} policy-simulation cases matched")
    if failures:
        raise SystemExit(1)
