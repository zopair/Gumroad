"""Behavior tests for each product-specific local workflow."""
import unittest
from jarvis_agents import run_agent

def content(report, heading):
    return next(item["content"] for item in report["sections"] if item["heading"] == heading)

class WorkflowOutputTests(unittest.TestCase):
    def test_rankmaster_creates_audience_specific_brief(self):
        result = run_agent("rankmaster-ai", {"topic":"ethical AI procurement","audience":"procurement leaders"})
        self.assertIn("procurement leaders", content(result, "Targeting")["audience"])
        self.assertEqual(len(content(result, "Content outline")), 5)

    def test_leadscout_deduplicates_and_requires_source_provenance(self):
        record = {"company":"Northstar","website":"https://northstar.example","source_url":"https://northstar.example/about"}
        result = run_agent("leadscout-bot", {"industry":"design","region":"London","prospects":[record,record,{"company":"Unverified"}]})
        self.assertEqual(len(content(result, "Qualified prospects")), 1)
        quality = content(result, "Data quality")
        self.assertEqual(quality["skipped_missing_or_invalid_source"], 1)
        self.assertEqual(quality["deduplicated"], 1)

    def test_tradetrend_computes_descriptive_price_metrics(self):
        result = run_agent("tradetrend-analyst", {"asset":"DEMO","timeframe":"1d","candles":[{"close":100},{"close":110},{"close":100}]})
        metrics = content(result, "Observed metrics")
        self.assertAlmostEqual(metrics["simple_moving_average"], 103.333333, places=5)
        self.assertEqual(metrics["period_change_percent"], 0.0)

    def test_docusense_returns_page_evidence_and_abstains_without_match(self):
        evidence = run_agent("docusense-support", {"query":"refund window","documents":[{"id":"terms","title":"Terms","chunks":[{"page":7,"text":"Refund requests must be made within thirty days."}]}]})
        self.assertEqual(content(evidence, "Evidence")[0]["page"], 7)
        abstain = run_agent("docusense-support", {"query":"refund","documents":[]})
        self.assertIn("Insufficient evidence", content(abstain, "Answer"))

    def test_codesentinel_flags_added_secret_and_dynamic_execution(self):
        result = run_agent("codesentinel", {"diff":"+password = \"supersecretvalue\"\n+eval(user_input)\n"})
        rules = {item["rule"] for item in content(result, "Findings")}
        self.assertIn("possible_secret", rules)
        self.assertIn("dynamic_eval", rules)

    def test_estateguard_attaches_line_references_to_clause_flags(self):
        result = run_agent("estateguard-ai", {"contract_text":"Agreement\nTenant pays rent monthly.\nTenant may terminate with notice."})
        findings = content(result, "Clause findings")
        self.assertEqual({item["line"] for item in findings}, {2,3})

    def test_socialsync_creates_unpublished_channel_drafts(self):
        result = run_agent("socialsync-ai", {"topic":"new service","audience":"founders","platforms":["linkedin","x"]})
        drafts = content(result, "Drafts")
        self.assertEqual(len(drafts), 2)
        self.assertTrue(all(item["status"].startswith("DRAFT") for item in drafts))

    def test_contentflip_preserves_supplied_transcript_words(self):
        result = run_agent("contentflip-ai", {"title":"A field guide","transcript":"Measure the baseline. Improve one step. Review the result."})
        article = content(result, "Article draft (Markdown)")
        self.assertIn("Measure the baseline.", article)
        self.assertIn("Review the result.", article)

    def test_marketmind_marks_missing_source_evidence(self):
        result = run_agent("marketmind-ai", {"market":"workflow tools","competitors":[{"name":"Example Rival","price":"$15"}]})
        competitor = content(result, "Competitor comparison")[0]
        self.assertEqual(competitor["evidence_status"], "unverified input")
        self.assertIsNone(competitor["source_url"])

    def test_tradetrend_rejects_non_positive_price(self):
        with self.assertRaises(ValueError):
            run_agent("tradetrend-analyst", {"asset":"DEMO","timeframe":"1d","candles":[{"close":0}]})

    def test_docusense_ranks_rare_query_terms_above_common_word_matches(self):
        result = run_agent("docusense-support", {"query":"refund chargeback deadline", "documents":[
            {"id":"generic","title":"Generic", "chunks":[{"page":1,"text":"Refund information and general customer support details."}]},
            {"id":"specific","title":"Specific", "chunks":[{"page":4,"text":"The chargeback deadline for a refund dispute is thirty days."}]}
        ]})
        evidence = content(result, "Evidence")
        self.assertEqual(evidence[0]["document_id"], "specific")
        self.assertEqual(evidence[0]["page"], 4)
        self.assertGreater(evidence[0]["relevance_score"], 0)

    def test_docusense_returns_stable_citations_and_bounded_evidence(self):
        result = run_agent("docusense-support", {"query":"retention policy", "documents":[
            {"id":"policy-1","title":"Retention", "chunks":[{"page":2,"text":"Records follow a retention policy for seven years."}]}
        ]})
        evidence = content(result, "Evidence")
        self.assertEqual(evidence[0]["citation"], "[policy-1, p. 2]")
        self.assertLessEqual(len(evidence), 5)

    def test_estateguard_scores_high_impact_deposit_terms_and_cites_excerpt(self):
        result = run_agent("estateguard-ai", {"contract_text":"Lease\nThe security deposit is non-refundable under all circumstances."})
        finding = content(result, "Clause findings")[0]
        self.assertEqual(finding["risk_level"], "high")
        self.assertEqual(finding["line"], 2)
        self.assertIn("non-refundable", finding["evidence"].lower())

    def test_estateguard_marks_review_scope_and_never_claims_legal_conclusion(self):
        result = run_agent("estateguard-ai", {"contract_text":"Agreement\nEither party may terminate with notice."})
        scope = content(result, "Review scope")
        self.assertIn("keyword", scope["method"].lower())
        self.assertIn("not legal advice", scope["disclaimer"].lower())

if __name__ == "__main__":
    unittest.main()


    def test_contentflip_parses_srt_cues_and_preserves_timestamps(self):
        subtitles = """1
00:00:01,250 --> 00:00:03,000
Welcome to the session.

2
00:00:04,500 --> 00:00:06,000
We explain <i>secure</i> document handling &amp; review.
"""
        result = run_agent("contentflip-ai", {"title":"Session guide","subtitle_text":subtitles})
        trace = content(result, "Source traceability")
        self.assertEqual(trace["source_type"], "user-supplied SRT/WebVTT subtitles")
        self.assertEqual(trace["subtitle_cues"], 2)
        cues = content(result, "Timed source segments")
        self.assertEqual(cues[0]["timestamp"], "00:00:01.250")
        self.assertIn("secure document handling & review", cues[1]["text"])
        self.assertIn("Welcome to the session.", content(result, "Article draft (Markdown)"))

    def test_contentflip_rejects_malformed_subtitle_file(self):
        with self.assertRaises(ValueError):
            run_agent("contentflip-ai", {"title":"Bad captions","subtitle_text":"not a subtitle file"})
