# JARVIS Agent Runtime — Local Edition

A lightweight, deterministic Python runtime for the first ten JARVIS product workflows. It uses only the Python standard library at runtime. No model key, database, container, browser automation, or hosted service is required for the baseline workflows.

## Status and honest scope

This is the first executable runtime foundation, not a claim that all ten commercial products are release-ready. The included workflows provide structured local analysis and drafting. Live search, transcription, semantic vector retrieval, model-generated copy, platform publishing, email sending, live trading, and code execution are intentionally not included.

## Requirements

- Python 3.11 or newer
- No third-party runtime dependencies

## Install

From this directory, create a virtual environment, activate it, then run: python -m pip install --no-deps -e .

## Run

Use jarvis-agents list to see the available products. Run an agent with: jarvis-agents run rankmaster-ai --input examples/rankmaster.json --output report.json

Or import the library: from jarvis_agents import run_agent

## Agent capabilities

| Agent | Local baseline workflow | Important boundary |
|---|---|---|
| RankMaster AI | SEO brief, outline, title/meta suggestions | No live SERP or keyword-volume claims |
| LeadScout Bot | Normalize, deduplicate, score supplied company records | No personal-profile scraping or email harvesting |
| TradeTrend Analyst | Statistics and scenarios from supplied closing prices | No live orders or investment advice |
| DocuSense Support | Lexical retrieval with document/page evidence | Not semantic RAG; no unsupported answer generation |
| SocialSync AI | Channel-specific post drafts and review checklist | Never publishes or schedules |
| MailForge Pro | Three-touch B2B email draft with evidence notes | Never sends email |
| ContentFlip AI | Transcript-to-article transformation | Does not transcribe or download media |
| EstateGuard AI | Keyword-based clause triage with excerpts | Not legal advice or enforceability analysis |
| CodeSentinel | Static checks on added diff lines | Never executes untrusted code |
| MarketMind AI | Competitor matrix and research-gap framework | Does not independently verify market data |

## Input and output contract

Every input is a UTF-8 JSON object. Every report includes schema_version, agent, title, summary, sections, warnings, and actions. actions is always empty in this edition. Inputs are validated and errors are returned without silently inventing missing facts.

## Privacy and cost

- Local workflows make no outbound network requests.
- No telemetry or analytics are collected.
- No API keys are required or read.
- The runtime does not persist input documents unless the user chooses an output file.
- No paid provider calls are made.

## Quality checks

Run python -m unittest discover -s tests -v and python -m compileall -q src.

See products.json for the product and SEO metadata baseline. Each commercial ZIP still needs its own upstream attribution, complete dependency/model/data/asset license audit, product-specific guide, and clean-install/package validation.
