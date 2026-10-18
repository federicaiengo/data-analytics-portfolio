"""Fictional tenant/document decision lab. Never use as real authorization middleware."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Document:
    doc_id: str
    tenant_id: str
    category: str
    approved_for_vendor: bool

DOCS = {
    "A-001": Document("A-001", "tenant_a", "billing", True),
    "A-002": Document("A-002", "tenant_a", "restricted", False),
    "A-003": Document("A-003", "tenant_a", "billing", True),
    "B-001": Document("B-001", "tenant_b", "billing", True),
    "B-002": Document("B-002", "tenant_b", "billing", False),
}
# Hypothetical scoped access matrix, not a real identity provider or policy source.
MEMBERSHIPS = {"S01": {"tenant_a"}, "S02": {"tenant_a"},
               "U04": {"tenant_a"}, "U05": {"tenant_b"}}
ROLE_ACTIONS = {"vendor_processor": {"read"}, "customer_operator": {"read"}}

# Deliberately invented approval registry for testing *binding* of approvals to
# principal, resource, tenant and time. A real system would query an authority.
APPROVALS = {
    "SIMULATED-APPROVAL-01": {"principal": "S01", "doc_id": "A-001", "tenant_id": "tenant_a",
                              "action": "read", "purpose": "approved_extraction", "expires_on": "2026-12-31", "approved_by": "U09"},
    "SIMULATED-APPROVAL-02": {"principal": "U04", "doc_id": "A-001", "tenant_id": "tenant_a",
                              "action": "read", "purpose": "approved_extraction", "expires_on": "2026-12-31", "approved_by": "U09"},
    "SIMULATED-APPROVAL-03": {"principal": "U05", "doc_id": "B-001", "tenant_id": "tenant_b",
                              "action": "read", "purpose": "approved_extraction", "expires_on": "2026-10-30", "approved_by": "U09"},
}


def evaluate_document(principal, role, doc_id, action, identities, *, evidence=None,
                      today="2026-10-14"):
    """ALLOW, DENY, or HOLD. HOLD never grants access."""
    # A duplicated or malformed identity directory must never select an
    # arbitrary matching account. Fail closed before consulting scope records.
    if not all(isinstance(value, str) for value in (principal, role, doc_id, action)):
        return "DENY"
    if not isinstance(identities, (list, tuple)):
        return "DENY"
    if evidence is not None and not isinstance(evidence, dict):
        return "DENY"
    matches = [x for x in identities if isinstance(x, dict) and x.get("id") == principal]
    if len(matches) != 1:
        return "DENY"
    item = matches[0]
    doc = DOCS.get(doc_id)
    if doc is None or item.get("role") != role:
        return "DENY"
    if item["status"] != "active" or item["expires_on"] <= today:
        return "DENY"
    if action not in ROLE_ACTIONS.get(role, set()):
        return "DENY"
    if doc.tenant_id not in MEMBERSHIPS.get(principal, set()):
        return "DENY"
    if doc.category != "billing" or not doc.approved_for_vendor:
        return "DENY"
    e = evidence or {}
    if e.get("authenticated") is not True:
        return "DENY"
    if item["kind"] == "human" and e.get("mfa_verified") is not True:
        return "DENY"
    if item["kind"] == "service" and e.get("service_verified") is not True:
        return "DENY"
    approval_id = e.get("approval_id")
    if not isinstance(approval_id, str):
        return "DENY"
    approval = APPROVALS.get(approval_id)
    if not approval:
        return "DENY"
    if (approval["principal"] != principal or approval["doc_id"] != doc_id
            or approval["tenant_id"] != doc.tenant_id or approval["action"] != action
            or approval["purpose"] != "approved_extraction"
            or approval["expires_on"] <= today or approval["approved_by"] == principal):
        return "DENY"
    if e.get("purpose") != approval["purpose"]:
        return "DENY"
    if role == "vendor_processor" and e.get("contract_active") is not True:
        return "DENY"
    if e.get("source_integrity_verified") is not True:
        return "HOLD"
    return "ALLOW"
