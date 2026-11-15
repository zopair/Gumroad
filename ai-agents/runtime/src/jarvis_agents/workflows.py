"""Ten deterministic product workflows; network/model integrations are optional add-ons."""
from __future__ import annotations
import math
import re
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlparse
from .validation import optional_text, report, required_text, section, sentences, text_list, words

def rankmaster(data: Mapping[str, Any]) -> dict[str, Any]:
    topic, audience = required_text(data, "topic"), required_text(data, "audience")
    keyword = optional_text(data, "primary_keyword", topic) or topic
    description = f"Learn how {keyword} can help {audience}. Explore practical considerations, useful steps, and questions to evaluate before choosing an approach."
    outline = [f"What {keyword} means for {audience}", "The main problems and search intents to address", "Options, trade-offs, and evaluation criteria", "A practical step-by-step approach", "Common questions and next steps"]
    return report(f"SEO brief: {topic}", f"Created a search-intent brief for '{topic}' aimed at {audience}.", [
        section("Targeting", {"topic": topic, "primary_keyword": keyword, "audience": audience, "intent": "informational / commercial investigation — validate against live SERP data"}),
        section("Suggested title", f"{keyword.title()}: A Practical Guide for {audience.title()}"), section("Meta description", description),
        section("Content outline", outline), section("On-page checklist", ["Use the primary phrase naturally", "Answer the searcher's main question early", "Add first-hand evidence and original examples", "Use descriptive headings", "Link to relevant supporting pages", "Review title and description against the live SERP"])
    ], ["No live search-volume, ranking, or SERP data was queried. Validate keyword intent and competition with a licensed search-data provider."])

def leadscout(data: Mapping[str, Any]) -> dict[str, Any]:
    industry, region = required_text(data, "industry"), required_text(data, "region")
    prospects = data.get("prospects", [])
    if not isinstance(prospects, list): raise ValueError("'prospects' must be a list of company records.")
    seen: set[str] = set(); qualified: list[dict[str, Any]] = []; skipped = 0
    for item in prospects:
        if not isinstance(item, Mapping): skipped += 1; continue
        company, source_url, website = (str(item.get(k, "")).strip() for k in ("company", "source_url", "website"))
        if not company or not source_url or urlparse(source_url).scheme not in {"http", "https"}: skipped += 1; continue
        key = re.sub(r"\W+", "", company.casefold())
        if key in seen: continue
        seen.add(key)
        score = 40 + (20 if website.startswith(("http://", "https://")) else 0) + (20 if item.get("description") else 0) + (20 if item.get("location") else 0)
        qualified.append({"company": company, "website": website or None, "source_url": source_url, "qualification_score": score, "score_basis": "Completeness of supplied company-level public evidence; not independently verified fit."})
    qualified.sort(key=lambda row: (-row["qualification_score"], row["company"].casefold()))
    return report(f"Business prospect shortlist: {industry}", f"Reviewed {len(prospects)} supplied records for {industry} in {region}; retained {len(qualified)} sourced company records.", [
        section("Qualified prospects", qualified), section("Data quality", {"input_records": len(prospects), "retained": len(qualified), "skipped_missing_or_invalid_source": skipped, "deduplicated": len(prospects) - skipped - len(qualified)})
    ], ["Only company-level records supplied by the user are processed. No personal-profile harvesting, authenticated scraping, or email verification is performed.", "Scores reflect record completeness, not purchase intent or verified fit."])

def tradetrend(data: Mapping[str, Any]) -> dict[str, Any]:
    asset, timeframe = required_text(data, "asset"), required_text(data, "timeframe")
    candles = data.get("candles", [])
    if not isinstance(candles, list) or not candles: raise ValueError("'candles' must be a non-empty list of objects with positive close values.")
    closes: list[float] = []
    for index, candle in enumerate(candles):
        if not isinstance(candle, Mapping): raise ValueError(f"candle {index} must be an object.")
        try: close = float(candle["close"])
        except (KeyError, TypeError, ValueError): raise ValueError(f"candle {index} requires a numeric close value.") from None
        if not math.isfinite(close) or close <= 0: raise ValueError(f"candle {index} close must be a finite positive number.")
        closes.append(close)
    returns = [(b / a) - 1 for a, b in zip(closes, closes[1:])]
    mean_return = sum(returns) / len(returns) if returns else 0.0
    volatility = math.sqrt(sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)) if len(returns) > 1 else 0.0
    return report(f"Market observation: {asset}", f"Computed descriptive statistics for {asset} using {len(closes)} supplied closing prices on timeframe {timeframe}.", [
        section("Observed metrics", {"observations": len(closes), "first_close": closes[0], "last_close": closes[-1], "simple_moving_average": round(sum(closes) / len(closes), 6), "period_change_percent": round((closes[-1] / closes[0] - 1) * 100, 4), "mean_period_return_percent": round(mean_return * 100, 4), "sample_return_volatility_percent": round(volatility * 100, 4)}),
        section("Scenario framework", {"bull_case": "Sustained closes above the observed average with improving breadth; requires independent confirmation.", "base_case": "Price remains near the observed average; monitor range and volatility.", "bear_case": "A sustained move below the observed average with rising volatility; define risk before acting."})
    ], ["Descriptive analysis of supplied data only; no live market feed was queried.", "This is not investment advice or a trade signal. No order is placed; verify data quality, fees, liquidity, and risk independently."])

def docusense(data: Mapping[str, Any]) -> dict[str, Any]:
    query = required_text(data, "query"); documents = data.get("documents", [])
    if not isinstance(documents, list): raise ValueError("'documents' must be a list.")
    query_terms = set(words(query)); matches: list[dict[str, Any]] = []
    for document in documents:
        if not isinstance(document, Mapping): continue
        doc_id, title = str(document.get("id", "unknown")), str(document.get("title", "Untitled document"))
        chunks = document.get("chunks", [])
        if not isinstance(chunks, list): continue
        for chunk in chunks:
            if not isinstance(chunk, Mapping): continue
            text = str(chunk.get("text", "")).strip(); overlap = len(query_terms & set(words(text)))
            if text and overlap: matches.append({"document_id": doc_id, "document_title": title, "page": chunk.get("page"), "evidence": text, "term_overlap": overlap})
    matches.sort(key=lambda row: (-row["term_overlap"], str(row["document_title"]), str(row["page"])))
    selected = matches[:5]
    answer = "Insufficient evidence in the supplied documents to answer this question." if not selected else "Relevant source passages were found. Review the cited evidence below; this local baseline does not generate unsupported claims."
    return report("Document question and evidence", f"Retrieved {len(selected)} evidence passage(s) for: {query}.", [section("Answer", answer), section("Evidence", selected)], ["Retrieval uses transparent lexical overlap only; this is not semantic vector search.", "Answers are limited to supplied text. Page references are only as accurate as the source metadata."])

def socialsync(data: Mapping[str, Any]) -> dict[str, Any]:
    topic, audience = required_text(data, "topic"), required_text(data, "audience")
    platforms = text_list(data.get("platforms", ["linkedin"]), "platforms")
    if not platforms: raise ValueError("At least one platform is required.")
    voice = optional_text(data, "brand_voice", "clear, useful, and specific"); drafts = []
    for platform in platforms:
        if platform.casefold() == "linkedin": copy = f"For {audience}: {topic} works best when the next step is clear. Start with one practical improvement, measure the result, and share what you learn."
        elif platform.casefold() in {"x", "twitter"}: copy = f"{topic}: make the next step practical. Choose one improvement, test it, and measure the result."
        else: copy = f"{topic}\n\nA practical idea for {audience}: start small, focus on one useful outcome, and measure what changes."
        drafts.append({"platform": platform, "copy": copy, "brand_voice": voice, "status": "DRAFT — HUMAN APPROVAL REQUIRED"})
    return report(f"Social content pack: {topic}", f"Prepared {len(drafts)} channel-specific draft(s) for {audience}.", [section("Drafts", drafts), section("Review checklist", ["Verify factual claims and links", "Check platform length and formatting", "Confirm brand voice and rights to all media", "Obtain human approval before publishing"])], ["Drafts are not published or scheduled. Human approval is required before publishing or scheduling any post."])

def mailforge(data: Mapping[str, Any]) -> dict[str, Any]:
    company, role, value = required_text(data, "company"), required_text(data, "recipient_role"), required_text(data, "value_proposition")
    evidence = text_list(data.get("evidence", []), "evidence")
    evidence_note = evidence[0] if evidence else "No verified company-specific evidence was supplied; personalize this line only after research."
    subject = f"A practical way to {value}"
    first = f"Hello,\n\nI am reaching out because teams in {role.lower()} roles may be looking to {value}. {evidence_note}\n\nWould it be useful if I shared a short overview of how this could work for {company}?\n\nBest,"
    follow = f"Hello,\n\nFollowing up on my note about how to {value}. If this is relevant to your priorities at {company}, I can send a concise example.\n\nBest,"
    close = f"Hello,\n\nI will close the loop here. If improving how you {value} becomes a priority, I would be glad to reconnect.\n\nBest,"
    return report(f"Outreach sequence: {company}", f"Drafted a three-touch B2B sequence for a {role} at {company}.", [section("Personalization evidence", evidence or ["No source evidence supplied — do not imply prior research or familiarity."]), section("Email sequence", [{"step": 1, "subject": subject, "body": first}, {"step": 2, "subject": f"Re: {subject}", "body": follow}, {"step": 3, "subject": f"Closing the loop — {value}", "body": close}]), section("Compliance review", ["Confirm lawful basis and applicable email marketing rules", "Identify the sender accurately", "Include a valid opt-out mechanism where required", "Verify every personalization claim"])], ["Messages are drafts only. Never send automatically; require human approval before sending. No deliverability or inbox-placement guarantee is made.", "Use only lawful, relevant business contact data and honor opt-out requests."])

def contentflip(data: Mapping[str, Any]) -> dict[str, Any]:
    title, transcript = required_text(data, "title"), required_text(data, "transcript"); parts = sentences(transcript)
    if not parts: raise ValueError("'transcript' must contain readable text.")
    body = "\n\n".join(parts[1:]) if len(parts) > 1 else "Expand this section with supporting examples and practical detail."
    article = f"# {title}\n\n## Introduction\n\n{parts[0]}\n\n## Key discussion\n\n{body}\n\n## Practical takeaway\n\nSummarize the most useful action a reader can take based on the source material."
    return report(f"Content repurposing: {title}", f"Converted {len(parts)} transcript sentence(s) into an editable article structure.", [section("Article draft (Markdown)", article), section("Source traceability", {"source_type": "user-supplied transcript", "sentence_count": len(parts), "requires_editorial_review": True})], ["This workflow transforms supplied text; it does not transcribe audio/video or download third-party media.", "Confirm ownership, permission, quotations, names, and factual accuracy before publication."])

def estateguard(data: Mapping[str, Any]) -> dict[str, Any]:
    text = required_text(data, "contract_text")
    patterns = [("deposit", r"\bdeposit\b", "Check amount, custody, deductions, and return deadline."), ("termination", r"\bterminat(?:e|ion|ed)\b", "Check notice period, permitted grounds, and cure rights."), ("rent_or_payment", r"\b(rent|payment|pay|fee)\b", "Check amount, due date, escalation, late fees, and payment method."), ("liability", r"\b(liability|indemnif(?:y|ication)|damages)\b", "Check scope, caps, exclusions, and mutuality."), ("renewal", r"\b(renew|renewal|extend|extension)\b", "Check renewal window, notice method, and pricing changes."), ("penalty", r"\b(penalty|fine|forfeit)\b", "Check trigger, calculation, enforceability, and proportionality.")]
    findings = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for clause, pattern, review in patterns:
            if re.search(pattern, line, flags=re.IGNORECASE): findings.append({"clause_type": clause, "line": line_no, "excerpt": line.strip()[:500], "review_prompt": review, "severity": "REVIEW"})
    return report("Contract review triage", f"Flagged {len(findings)} clause reference(s) for human review.", [section("Clause findings", findings), section("Review limitations", ["The scan is keyword-based and may miss clauses expressed differently.", "Compare the full agreement, schedules, amendments, and governing-law clause.", "Escalate ambiguous or high-impact provisions to a qualified local lawyer."])], ["This tool provides document triage, not legal advice, legal interpretation, or an enforceability opinion. Jurisdiction-specific review is required."])

def codesentinel(data: Mapping[str, Any]) -> dict[str, Any]:
    diff = required_text(data, "diff")
    rules = [
        ("possible_secret", re.compile(r"""(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['"][^'"]{6,}['"]"""), "high", "Possible hard-coded credential; rotate if real and move secrets to a secure runtime store."),
        ("dynamic_eval", re.compile(r"\b(eval|exec)\s*\("), "high", "Dynamic code execution can enable injection; remove or tightly constrain the execution path."),
        ("shell_execution", re.compile(r"(?i)(shell\s*=\s*true|os\.system\s*\(|subprocess\.(?:run|Popen)\s*\()"), "medium", "Review command construction, argument separation, and untrusted input boundaries."),
        ("sql_concatenation", re.compile(r"""(?i)(SELECT|UPDATE|INSERT|DELETE).*(\+|\.format\(|f['"])"""), "medium", "Review whether user-controlled values are concatenated into SQL; use parameterized queries."),
    ]
    findings = []
    for line_no, line in enumerate(diff.splitlines(), start=1):
        if not line.startswith("+") or line.startswith("+++"): continue
        added = line[1:]
        for rule, pattern, severity, recommendation in rules:
            if pattern.search(added): findings.append({"rule": rule, "diff_line": line_no, "severity": severity, "evidence": added[:400], "recommendation": recommendation})
    return report("Code review findings", f"Inspected added diff lines and identified {len(findings)} candidate issue(s).", [section("Findings", findings), section("Review scope", {"added_lines": sum(1 for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")), "analysis_mode": "static pattern checks", "execution": "disabled"})], ["Static pattern checks are incomplete and may produce false positives or miss vulnerabilities.", "Untrusted source code is never executed. Confirm findings with language-aware analysis and human review."])

def marketmind(data: Mapping[str, Any]) -> dict[str, Any]:
    market, competitors = required_text(data, "market"), data.get("competitors", [])
    if not isinstance(competitors, list): raise ValueError("'competitors' must be a list.")
    rows, missing_sources = [], 0
    for item in competitors:
        if not isinstance(item, Mapping): continue
        name, source_url = str(item.get("name", "")).strip(), str(item.get("source_url", "")).strip()
        if not name: continue
        valid_source = urlparse(source_url).scheme in {"http", "https"}
        if not valid_source: missing_sources += 1
        rows.append({"competitor": name, "positioning": item.get("positioning"), "price": item.get("price"), "source_url": source_url if valid_source else None, "evidence_status": "source supplied" if valid_source else "unverified input"})
    rows.sort(key=lambda row: row["competitor"].casefold())
    return report(f"Market intelligence brief: {market}", f"Structured {len(rows)} competitor record(s) for the {market} market.", [section("Competitor comparison", rows), section("Evidence gaps", {"competitors_without_valid_source": missing_sources, "research_needed": ["Validate current pricing and plan limits", "Capture dated source evidence for positioning claims", "Compare target segments and distribution channels", "Separate observed facts from hypotheses"]}), section("Initial SWOT prompts", {"strengths": "Identify capabilities supported by customer evidence.", "weaknesses": "Identify gaps in product, reach, or economics.", "opportunities": "Look for underserved segments and unmet workflows.", "threats": "Assess substitutes, switching costs, regulation, and platform dependence."})], ["This report structures supplied inputs; it does not independently verify market coverage, pricing, or competitor claims.", "Add dated, attributable sources before relying on findings for investment or strategic decisions."])
