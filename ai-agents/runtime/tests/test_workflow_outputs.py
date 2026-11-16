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


    def test_codesentinel_scans_multiple_source_files_with_file_and_line_evidence(self):
        result = run_agent("codesentinel", {"files":[
            {"path":"src/api.py","language":"python","content":"import yaml\nconfig = yaml.load(request.data)\n"},
            {"path":"src/client.py","language":"python","content":"requests.get(url, verify=False)\n"}
        ]})
        findings = content(result, "Findings")
        self.assertEqual({item["file_path"] for item in findings}, {"src/api.py", "src/client.py"})
        self.assertTrue(all(item["line"] > 0 and item["evidence"] for item in findings))
        self.assertIn("unsafe_yaml_load", {item["rule"] for item in findings})
        self.assertIn("tls_verification_disabled", {item["rule"] for item in findings})

    def test_codesentinel_detects_insecure_deserialization_and_shell_true(self):
        result = run_agent("codesentinel", {"files":[
            {"path":"worker.py","content":"import pickle\npayload = pickle.loads(blob)\nsubprocess.run(command, shell=True)\n"}
        ]})
        rules = {item["rule"] for item in content(result, "Findings")}
        self.assertIn("unsafe_deserialization", rules)
        self.assertIn("shell_execution", rules)

    def test_codesentinel_preserves_legacy_diff_and_does_not_flag_removed_lines(self):
        result = run_agent("codesentinel", {"diff":"-eval(old_input)\n+safe = True\n"})
        self.assertEqual(content(result, "Findings"), [])


    def test_codesentinel_enforces_per_file_scan_limit(self):
        with self.assertRaises(ValueError):
            run_agent("codesentinel", {"files":[{"path":"large.py","content":"x" * 200001}]})


    def test_rankmaster_builds_deduplicated_keyword_cluster_and_placement_map(self):
        result = run_agent("rankmaster-ai", {
            "topic":"AI procurement", "audience":"procurement teams",
            "primary_keyword":"AI procurement",
            "secondary_keywords":["vendor risk","AI procurement","supplier review","  "],
            "search_intent":"commercial"
        })
        strategy = content(result, "Keyword strategy")
        self.assertEqual(strategy["secondary_keywords"], ["vendor risk", "supplier review"])
        self.assertEqual(strategy["search_intent"], "commercial")
        self.assertIn("title", strategy["recommended_placements"])
        self.assertIn("supplier review", " ".join(strategy["recommended_placements"]["headings"]))

    def test_rankmaster_rejects_oversized_keyword_clusters(self):
        with self.assertRaises(ValueError):
            run_agent("rankmaster-ai", {
                "topic":"AI procurement", "audience":"procurement teams",
                "secondary_keywords":[f"keyword-{i}" for i in range(21)]
            })


if __name__ == "__main__":
    unittest.main()
