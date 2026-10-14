"""Unit tests for a simulated policy; not evidence of an installed IAM safeguard."""
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parent
iam = SourceFileLoader("iam", str(ROOT / "04_EVALUATE_ACCESS.py")).load_module()
people = iam.load_fixture("04_IDENTITY_FIXTURES.json")["identities"]
cases = iam.load_fixture("04_ACCESS_SCENARIOS.json")["cases"]

class IAMAccessTests(unittest.TestCase):
    def test_fixture_shape(self):
        iam.verify_fixtures(people, cases)

    def test_all_24_expected_decisions(self):
        for c in cases:
            with self.subTest(case=c["id"]):
                self.assertEqual(iam.decide(c["principal"], c["resource"],
                    c["action"], people, flags=c.get("flags")), c["expected"])

    def test_unknown_identity_defaults_to_deny(self):
        self.assertEqual(iam.decide("U99", "analytics_summary", "read", people), "DENY")

    def test_valid_identity_does_not_grant_db_access(self):
        self.assertEqual(iam.decide("S01", "production_database", "read", people), "DENY")

    def test_expired_token_does_not_authorize(self):
        self.assertEqual(iam.decide("S02", "staging_selected", "read", people), "DENY")

    def test_vendor_human_not_service_processor(self):
        self.assertEqual(iam.decide("U11", "processing_endpoint", "call", people), "DENY")

    def test_vendor_provenance_uncertain_escalates(self):
        self.assertEqual(iam.decide("S01", "staging_selected", "read", people,
            flags={**cases[2]["flags"], "source_verified": False}), "ESCALATE")

    def test_escalation_cannot_override_expiry(self):
        self.assertEqual(iam.decide("S02", "staging_selected", "read", people,
            flags={"source_verified": False}), "DENY")

    def test_no_vendor_contract(self):
        self.assertEqual(iam.decide("S01", "staging_selected", "read", people,
            flags={"contract_active": False}), "DENY")

    def test_no_human_mfa(self):
        self.assertEqual(iam.decide("U04", "approved_document", "read", people,
            flags={"mfa": False}), "DENY")

    def test_no_self_approval(self):
        self.assertEqual(iam.decide("U09", "vendor_access_request", "approve", people,
            flags={"requester": "U09"}), "DENY")

    def test_independent_reviewer(self):
        self.assertEqual(iam.decide("U09", "vendor_access_request", "approve", people,
            flags=cases[11]["flags"]), "ALLOW")

    def test_all_restricted_roles_fail_without_authentication(self):
        for actor in ("U01", "U04", "U09", "S01", "S03"):
            with self.subTest(actor=actor):
                self.assertEqual(iam.decide(actor, "staging_selected", "read", people,
                    flags={"authenticated": False}), "DENY")

    def test_default_request_is_denied(self):
        self.assertEqual(iam.decide("S01", "staging_selected", "read", people), "DENY")

    def test_expiry_boundary_denied(self):
        self.assertEqual(iam.decide("S01", "staging_selected", "read", people,
            today="2026-11-01"), "DENY")

    def test_no_unlisted_permission(self):
        self.assertEqual(iam.decide("U09", "integration_config", "manage", people), "DENY")

if __name__ == "__main__":
    unittest.main()
