import unittest
from src.analyze_visibility import calculate_metrics

class TestMetrics(unittest.TestCase):
    def test_metrics(self):
        rows = [
            {"query_id":"q1","target_mentioned":"1","target_cited":"1","cited_domains":"a.com|b.com","competitor_mentions":"C1"},
            {"query_id":"q1","target_mentioned":"1","target_cited":"0","cited_domains":"a.com","competitor_mentions":""},
            {"query_id":"q2","target_mentioned":"0","target_cited":"0","cited_domains":"","competitor_mentions":"C2"},
        ]
        m = calculate_metrics(rows)
        self.assertEqual(m["observations"], 3)
        self.assertAlmostEqual(m["mention_rate"], 2/3)
        self.assertAlmostEqual(m["citation_rate"], 1/3)
        self.assertAlmostEqual(m["source_diversity"], 2/3)
        self.assertEqual(m["retrieval_consistency"], 1.0)
        self.assertAlmostEqual(m["share_of_voice"], 0.5)

if __name__ == "__main__":
    unittest.main()
