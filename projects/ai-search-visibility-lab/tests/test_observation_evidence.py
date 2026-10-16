"""Safety gates for real AI response evidence, using fabricated inputs only."""
import unittest

from src.validate_observation_evidence import validate_observations


VALID = {
    "run_id": "invented-run-1", "observed_at_utc": "2026-10-01T12:00:00Z",
    "platform": "Demo", "model": "mock-1", "query_id": "Q1",
    "query_text": "Fabricated prompt", "target_brand": "InventedBrand",
    "target_mentioned": "1", "target_cited": "1",
    "cited_urls": "https://example.org/public|https://example.edu/other",
}


class ObservationEvidenceTests(unittest.TestCase):
    def test_valid_fabricated_observation(self):
        self.assertEqual(validate_observations([VALID]), 1)

    def test_empty_observations_not_misreported_as_zero_visibility(self):
        with self.assertRaisesRegex(ValueError, "No observed responses"):
            validate_observations([])

    def test_citation_requires_checkable_url(self):
        with self.assertRaisesRegex(ValueError, "Citation marked true"):
            validate_observations([{**VALID, "cited_urls": ""}])

    def test_unusable_citation_urls_rejected(self):
        for url in ("not-a-url", "ftp://example.org/x", "https://", "//example.org/x"):
            with self.subTest(url=url):
                with self.assertRaisesRegex(ValueError, "Invalid citation URL"):
                    validate_observations([{**VALID, "cited_urls": url}])

    def test_observation_utc_is_required(self):
        for timestamp in ("not-a-date", "2026-10-01T12:00:00", "2026-10-01T12:00:00+02:00"):
            with self.subTest(timestamp=timestamp):
                with self.assertRaisesRegex(ValueError, "timestamp"):
                    validate_observations([{**VALID, "observed_at_utc": timestamp}])

    def test_bad_rows_and_missing_identifiers_rejected(self):
        with self.assertRaisesRegex(ValueError, "Malformed observation"):
            validate_observations([{**VALID, None: ["extra"]}])
        with self.assertRaisesRegex(ValueError, "Missing required query_id"):
            validate_observations([{**VALID, "query_id": ""}])

    def test_zero_target_citation_may_include_third_party_urls(self):
        self.assertEqual(validate_observations([{**VALID, "target_cited": "0"}]), 1)


if __name__ == "__main__":
    unittest.main()
