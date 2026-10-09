import unittest
from src.analyze_visibility import calculate_metrics

class TestMetrics(unittest.TestCase):
    def test_metrics(self):
        rows = [
            {"platform":"Demo","model":"v1","target_brand":"Brand","query_text":"Question one","query_id":"q1","target_mentioned":"1","target_cited":"1","cited_domains":"a.com|b.com","competitor_mentions":"C1"},
            {"platform":"Demo","model":"v1","target_brand":"Brand","query_text":"Question one","query_id":"q1","target_mentioned":"1","target_cited":"0","cited_domains":"a.com","competitor_mentions":""},
            {"platform":"Demo","model":"v1","target_brand":"Brand","query_text":"Question two","query_id":"q2","target_mentioned":"0","target_cited":"0","cited_domains":"","competitor_mentions":"C2"},
        ]
        m = calculate_metrics(rows)
        self.assertEqual(m["observations"], 3)
        self.assertAlmostEqual(m["mention_rate"], 2/3)
        self.assertAlmostEqual(m["citation_rate"], 1/3)
        self.assertAlmostEqual(m["source_diversity"], 2/3)
        self.assertAlmostEqual(m["retrieval_consistency"], 1.0)
        self.assertEqual(m["repeated_query_groups"], 1)
        self.assertAlmostEqual(m["share_of_voice"], 0.5)

    def test_one_observation_does_not_prove_consistency(self):
        rows = [{"platform": "Engine", "model": "m1", "query_id": "q1", "query_text": "Question",
                 "target_brand": "Brand", "target_mentioned": "1"}]
        m = calculate_metrics(rows)
        self.assertIsNone(m["retrieval_consistency"])
        self.assertEqual(m["repeated_query_groups"], 0)

    def test_mixed_models_are_not_equivalent_replicates(self):
        rows = [
            {"platform": "Engine", "model": model, "query_id": "q1", "query_text": "Question",
             "target_brand": "Brand", "target_mentioned": mentioned}
            for model, mentioned in (("m1", "0"), ("m2", "1"))
        ]
        m = calculate_metrics(rows)
        self.assertIsNone(m["retrieval_consistency"])

    def test_identical_protocol_can_be_inconsistent(self):
        rows = [
            {"platform": "Engine", "model": "m1", "query_id": "q1", "query_text": "Question",
             "target_brand": "Brand", "target_mentioned": mentioned}
            for mentioned in ("0", "1")
        ]
        m = calculate_metrics(rows)
        self.assertEqual(m["repeated_query_groups"], 1)
        self.assertEqual(m["retrieval_consistency"], 0.0)

    def test_query_identifiers_required(self):
        with self.assertRaises(ValueError):
            calculate_metrics([{"target_brand": "Brand", "target_mentioned": "1"}])

    def test_no_observations_is_not_repeatability_zero(self):
        m = calculate_metrics([])
        self.assertEqual(m["observations"], 0)
        self.assertIsNone(m["retrieval_consistency"])


if __name__ == "__main__":
    unittest.main()
