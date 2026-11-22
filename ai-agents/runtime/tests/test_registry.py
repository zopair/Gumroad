"""Contract tests for the ten independently addressable JARVIS agents."""
import unittest

from jarvis_agents import AGENT_SLUGS, run_agent


FIXTURES = {
    "rankmaster-ai": {"topic": "sustainable office furniture", "audience": "small business owners", "primary_keyword": "sustainable office furniture"},
    "leadscout-bot": {"industry": "commercial interior design", "region": "London", "prospects": [{"company": "Northstar Studio", "website": "https://example.com", "source_url": "https://example.com/about"}]},
    "tradetrend-analyst": {"asset": "DEMO", "timeframe": "1d", "candles": [{"close": 100}, {"close": 102}, {"close": 101}, {"close": 104}]},
    "docusense-support": {"query": "refund period", "documents": [{"id": "policy", "title": "Returns policy", "chunks": [{"page": 2, "text": "Customers may request a refund within 30 days of purchase."}]}]},
    "socialsync-ai": {"topic": "product launch", "audience": "founders", "platforms": ["linkedin", "x"], "brand_voice": "clear and useful"},
    "mailforge-pro": {"company": "Northstar Studio", "recipient_role": "Operations Director", "value_proposition": "reduce manual reporting", "evidence": ["The company publishes an annual operations report."]},
    "contentflip-ai": {"title": "A practical guide", "transcript": "First, define the problem. Next, compare the available options. Finally, measure the result."},
    "estateguard-ai": {"contract_text": "The tenant shall pay a deposit of 2000 USD. The agreement may be terminated with 30 days written notice."},
    "codesentinel": {"diff": "diff --git a/app.py b/app.py\n+password = \"secret_123456789\"\n+eval(user_input)\n"},
    "marketmind-ai": {"market": "workflow automation", "competitors": [{"name": "Alpha", "source_url": "https://example.com/alpha", "price": "$20", "positioning": "simple automation"}]},
}


class RegistryContractTests(unittest.TestCase):
    def test_registry_contains_exactly_the_ten_approved_products(self):
        self.assertEqual(len(AGENT_SLUGS), 10)
        self.assertEqual(set(FIXTURES), set(AGENT_SLUGS))

    def test_every_agent_returns_the_shared_report_contract(self):
        for slug, payload in FIXTURES.items():
            with self.subTest(agent=slug):
                report = run_agent(slug, payload)
                self.assertEqual(report["agent"], slug)
                self.assertTrue(report["title"])
                self.assertTrue(report["summary"])
                self.assertIsInstance(report["sections"], list)
                self.assertIsInstance(report["warnings"], list)
                self.assertEqual(report["actions"], [])

    def test_results_are_deterministic_for_identical_inputs(self):
        for slug, payload in FIXTURES.items():
            with self.subTest(agent=slug):
                self.assertEqual(run_agent(slug, payload), run_agent(slug, payload))

    def test_unknown_agent_is_rejected(self):
        with self.assertRaises(ValueError):
            run_agent("not-a-real-agent", {})

    def test_missing_required_input_is_rejected_with_actionable_error(self):
        with self.assertRaises(ValueError):
            run_agent("rankmaster-ai", {})


if __name__ == "__main__":
    unittest.main()
