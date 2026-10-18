"""Unit tests on synthetic fixtures only, not tested production isolation."""
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
ROOT = Path(__file__).resolve().parent
policy = SourceFileLoader("policy", str(ROOT / "05_DOCUMENT_SCOPE_POLICY.py")).load_module()
import json
identities = json.loads((ROOT / "04_IDENTITY_FIXTURES.json").read_text())["identities"]

VENDOR_OK = {"authenticated": True, "service_verified": True,
             "approval_id": "SIMULATED-APPROVAL-01", "purpose": "approved_extraction",
             "contract_active": True, "source_integrity_verified": True}
HUMAN_OK = {"authenticated": True, "mfa_verified": True,
            "approval_id": "SIMULATED-APPROVAL-02", "purpose": "approved_extraction",
            "source_integrity_verified": True}

def decide(who="S01", role="vendor_processor", doc="A-001", action="read",
           evidence=None, today="2026-10-14"):
    if evidence is None: evidence = VENDOR_OK
    return policy.evaluate_document(who, role, doc, action, identities,
                                    evidence=evidence, today=today)

class DocumentScopeTests(unittest.TestCase):
    def test_allowed_scoped_vendor_document(self):
        self.assertEqual(decide(), "ALLOW")

    def test_vendor_cannot_read_other_tenant(self):
        self.assertEqual(decide(doc="B-001"), "DENY")

    def test_unknown_document(self):
        self.assertEqual(decide(doc="UNKNOWN"), "DENY")

    def test_vendor_cannot_read_restricted_data(self):
        self.assertEqual(decide(doc="A-002"), "DENY")

    def test_tenant_b_operator_only_in_tenant_b(self):
        tenant_b_evidence = {**HUMAN_OK, "approval_id": "SIMULATED-APPROVAL-03"}
        self.assertEqual(decide("U05", "customer_operator", "B-001", evidence=tenant_b_evidence), "ALLOW")
        self.assertEqual(decide("U05", "customer_operator", "A-001", evidence=tenant_b_evidence), "DENY")

    def test_operator_cannot_call_vendor_role(self):
        self.assertEqual(decide("U04", "vendor_processor", "A-001", evidence=HUMAN_OK), "DENY")

    def test_no_evidence(self):
        self.assertEqual(decide(evidence={}), "DENY")

    def test_absent_contract(self):
        self.assertEqual(decide(evidence={**VENDOR_OK, "contract_active": False}), "DENY")

    def test_missing_approval_id(self):
        self.assertEqual(decide(evidence={**VENDOR_OK, "approval_id": ""}), "DENY")

    def test_unapproved_purpose(self):
        self.assertEqual(decide(evidence={**VENDOR_OK, "purpose": "general_analysis"}), "DENY")

    def test_doubtful_provenance_is_hold_not_approve(self):
        self.assertEqual(decide(evidence={**VENDOR_OK, "source_integrity_verified": False}), "HOLD")

    def test_source_unverified_does_not_override_out_of_scope(self):
        self.assertEqual(decide(doc="B-001", evidence={**VENDOR_OK,
                         "source_integrity_verified": False}), "DENY")

    def test_human_mfa_required(self):
        self.assertEqual(decide("U04", "customer_operator", "A-001",
                          evidence={**HUMAN_OK, "mfa_verified": False}), "DENY")

    def test_expired_service_access(self):
        self.assertEqual(decide("S01", today="2026-11-01"), "DENY")

    def test_expired_identity_blocked(self):
        self.assertEqual(decide("S02"), "DENY")

    def test_disabled_identity_blocked(self):
        self.assertEqual(decide("U14", "data_analyst", "A-001"), "DENY")

    def test_unauthorized_action(self):
        self.assertEqual(decide(action="delete"), "DENY")

    def test_unapproved_tenant_b_document(self):
        self.assertEqual(decide("U05", "customer_operator", "B-002", evidence=HUMAN_OK), "DENY")

    def test_same_tenant_approved_category_other_document_denied(self):
        self.assertEqual(decide(doc="A-003", evidence=VENDOR_OK), "DENY")

    def test_unhashable_approval_id_denied(self):
        self.assertEqual(decide(evidence={**VENDOR_OK, "approval_id": ["not-an-id"]}), "DENY")

    def test_unhashable_document_identifier_denied(self):
        self.assertEqual(decide(doc=["A-001"]), "DENY")

    def test_duplicate_subject_identity_denied(self):
        duplicates = identities + [dict(next(i for i in identities if i["id"] == "S01"))]
        self.assertEqual(
            policy.evaluate_document("S01", "vendor_processor", "A-001", "read",
                                     duplicates, evidence=VENDOR_OK),
            "DENY",
        )

    def test_non_mapping_evidence_denied(self):
        self.assertEqual(decide(evidence=["authenticated", "approval_id"]), "DENY")

    def test_invalid_evaluation_date_denied(self):
        for today in ("2026-10-4", "not-a-date", "2026-02-30", None, ["2026-10-14"]):
            with self.subTest(today=today):
                self.assertEqual(decide(today=today), "DENY")

    def test_malformed_identity_expiry_denied(self):
        for expiry in ("not-a-date", None, "2026-2-14"):
            with self.subTest(expiry=expiry):
                entries = [{**i, "expires_on": expiry} if i["id"] == "S01" else i
                           for i in identities]
                self.assertEqual(
                    policy.evaluate_document("S01", "vendor_processor", "A-001", "read",
                                             entries, evidence=VENDOR_OK), "DENY")

    def test_malformed_approval_expiry_denied(self):
        from unittest.mock import patch
        for expiry in ("not-a-date", None, "2026-2-14"):
            with self.subTest(expiry=expiry):
                fake_id = "SYNTHETIC-BAD-EXPIRY"
                bad_approval = {**policy.APPROVALS["SIMULATED-APPROVAL-01"],
                                "expires_on": expiry}
                with patch.dict(policy.APPROVALS, {fake_id: bad_approval}):
                    evidence = {**VENDOR_OK, "approval_id": fake_id}
                    self.assertEqual(decide(evidence=evidence), "DENY")

    def test_unknown_approval_id_denied(self):
        self.assertEqual(decide(evidence={**VENDOR_OK, "approval_id": "UNRECOGNIZED"}), "DENY")

    def test_other_principal_approval_cannot_be_borrowed(self):
        self.assertEqual(decide("U05", "customer_operator", "B-001", evidence=HUMAN_OK), "DENY")

    def test_approval_scope_cannot_change_document(self):
        self.assertEqual(decide("U04", "customer_operator", "B-001", evidence=HUMAN_OK), "DENY")

    def test_approval_expires_before_identity(self):
        tenant_b = {**HUMAN_OK, "approval_id": "SIMULATED-APPROVAL-03"}
        self.assertEqual(decide("U05", "customer_operator", "B-001",
                                evidence=tenant_b, today="2026-10-30"), "DENY")

    def test_vendor_cannot_borrow_human_approval(self):
        self.assertEqual(decide(evidence={**VENDOR_OK, "approval_id": "SIMULATED-APPROVAL-02"}), "DENY")

if __name__ == "__main__": unittest.main()
