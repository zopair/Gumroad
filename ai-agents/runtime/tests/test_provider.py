"""Tests for explicit provider opt-in and output safety."""
import json
import unittest
from jarvis_agents import run_agent
from jarvis_agents.providers import OpenAICompatibleProvider

class FakeProvider:
    def __init__(self, response): self.response, self.called = response, False
    def complete(self, messages): self.called, self.messages = True, messages; return self.response

class ProviderTests(unittest.TestCase):
    def test_provider_requires_https_outside_localhost(self):
        with self.assertRaises(ValueError): OpenAICompatibleProvider(api_key="test", model="test-model", base_url="http://example.com/v1/chat/completions")
    def test_provider_rejects_empty_credentials(self):
        with self.assertRaises(ValueError): OpenAICompatibleProvider(api_key="", model="test-model")
    def test_provider_cannot_be_called_implicitly(self):
        provider = FakeProvider("{}")
        run_agent("rankmaster-ai", {"topic":"topic","audience":"audience"})
        self.assertFalse(provider.called)
    def test_ai_enhancement_preserves_safety_contract_and_disclosures(self):
        provider = FakeProvider(json.dumps({"title":"Refined title","summary":"Refined summary","sections":[{"heading":"Brief","content":"Evidence-constrained copy"}]}))
        result = run_agent("rankmaster-ai", {"topic":"topic","audience":"audience"}, provider=provider)
        self.assertTrue(provider.called)
        self.assertEqual(result["title"], "Refined title")
        self.assertEqual(result["actions"], [])
        self.assertTrue(any("third-party" in warning for warning in result["warnings"]))
    def test_invalid_ai_response_is_rejected(self):
        with self.assertRaises(ValueError): run_agent("rankmaster-ai", {"topic":"topic","audience":"audience"}, provider=FakeProvider("not json"))

if __name__ == "__main__": unittest.main()
