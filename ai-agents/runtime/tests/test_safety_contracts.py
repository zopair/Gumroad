"""Safety invariants: analysis and drafting only; no external side effects."""
import unittest

from jarvis_agents import run_agent


class SafetyContractTests(unittest.TestCase):
    def test_social_content_is_never_published_automatically(self):
        result = run_agent("socialsync-ai", {"topic": "launch", "audience": "customers", "platforms": ["linkedin"]})
        self.assertEqual(result["actions"], [])
        self.assertIn("approval", " ".join(result["warnings"]).lower())

    def test_email_is_drafted_but_never_sent(self):
        result = run_agent("mailforge-pro", {"company": "Example Co", "recipient_role": "Founder", "value_proposition": "save time"})
        self.assertEqual(result["actions"], [])
        self.assertIn("send", " ".join(result["warnings"]).lower())

    def test_trading_analysis_never_places_live_orders(self):
        result = run_agent("tradetrend-analyst", {"asset": "DEMO", "timeframe": "1d", "candles": [{"close": 10}, {"close": 11}]})
        self.assertEqual(result["actions"], [])
        self.assertIn("not", " ".join(result["warnings"]).lower())

    def test_code_review_never_executes_untrusted_code(self):
        result = run_agent("codesentinel", {"diff": "+print('hello')"})
        self.assertEqual(result["actions"], [])
        self.assertIn("execute", " ".join(result["warnings"]).lower())

    def test_contract_review_disclaims_legal_advice(self):
        result = run_agent("estateguard-ai", {"contract_text": "The tenant shall pay rent monthly."})
        self.assertIn("legal", " ".join(result["warnings"]).lower())


if __name__ == "__main__":
    unittest.main()
