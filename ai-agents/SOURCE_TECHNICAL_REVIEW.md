# JARVIS AI Agents — Technical Source Qualification Review

**Inspection date:** 2026-11-15  
**Method:** GitHub repository metadata, recursive source tree, README, top-level LICENSE, and branch HEAD.  
**Important:** This is a source-selection review, not a complete legal/security audit. No source code has been copied into the commercial packages.

## Executive decision

The ten repositories have eligible top-level MIT or Apache-2.0 license texts, but none should be redistributed unchanged as a finished JARVIS product. Several are prototypes, agent skill packs, tutorial projects, or large applications with external paid services. The right strategy is **selective extraction + original product engineering**, not blind cloning and logo replacement.

| Product | Pinned upstream HEAD | Observed technical shape | Serverless/lightweight fit | Decision |
|---|---|---|---|---|
| RankMaster AI | `humanswith-ai/contentos-agent-lite@3b204b05bac946e3cb7cca96e24e31a869192888` | Python 3.10+, content-agent workflow/skills, optional research providers, local deterministic scoring | Strong for local/agent-skill core; not a hosted SEO SaaS by itself | Keep as workflow foundation; build a thin standalone UI/API only if required |
| LeadScout Bot | `GURPREETKAURJETHRA/AI-Lead-Generation-Agent@49254cb4ce9178dca207af595f2fe2762fb0c121` | 9-file Python project; Quora discovery/extraction; Firecrawl, Phidata, Composio Google Sheets, GPT-4o | Poor as-is: external services and account/API dependencies | Do not ship unchanged; replace source acquisition with compliant provider adapters and company-level public data |
| TradeTrend Analyst | `TauricResearch/TradingAgents@9fa1196fffbcfd9de5146d2dd2869df84ab99838` | 213 files; multi-agent framework; Docker/Compose; market-data and LLM provider configuration | Poor as-is for serverless; research runs can be long and provider-intensive | Extract analytical workflow selectively; first release is report + paper-trading only |
| DocuSense Support | `LeonAchata/DocuChat-AI@0cb4d059542c57e2c07cdd168169e13132270e45` | FastAPI + Next.js, LangGraph, Postgres/pgvector, ONNX embeddings, hybrid retrieval/reranking | Good modular architecture but heavier than a minimal serverless app; Postgres/pgvector service required for full stack | Retain retrieval/citation design; ship local SQLite/FAISS edition first, optional hosted adapter later |
| SocialSync AI | `langchain-ai/social-media-agent@ec9d0ece32bfad999954e45b57f9325521c4e3d9` | 254 files; LangGraph server; Anthropic, Firecrawl, Arcade, LangSmith; optional Supabase/Slack/GitHub | Poor as-is for low-cost self-contained deployment | Reuse human-approval workflow and content transformation; avoid shipping unnecessary integrations |
| MailForge Pro | `The-Pocket/PocketFlow-Tutorial-Cold-Email-Personalization@200903e33e7756a880160f8b7c5d6e5dd51794a6` | 18-file tutorial; personalized opener generator; setup requires implementing `call_llm` and `search_web`; Streamlit/batch CSV | Lightweight potential, but incomplete out of the box | Treat as tutorial reference only; implement provider interfaces, evidence-backed personalization, templates and tests |
| ContentFlip AI | `DEKVIW/video-to-article@d08a20493da7a1cfdb19c270108c1159e93247b7` | 87 files; Windows GUI, FFmpeg, yt-dlp, local ASR (FunASR/Whisper); model download can be ~1GB | Not serverless/lightweight in its default local-ASR mode | Rebuild as on-demand local transcription pipeline; optional external transcription adapter; audit binary/model licenses |
| EstateGuard AI | `gautampapat/Smart-PDF-Contract-Analyzer@9d0355378dd8e0e5bd5eef318ab272c61b1caeff` | 13-file Streamlit app; PDF/OCR, local embeddings/reranking, Chroma, Gemini/Groq endpoints | Moderate local footprint; not serverless as-is | Keep extraction and risk-review concepts; add evidence citations, deletion, uncertainty and jurisdiction boundaries |
| CodeSentinel | `alibaba/open-code-review@7e5ce06c88de5ce81df5dc4f24e2e485b517fae8` | 1,216 files; Go CLI/agent ecosystem, platform packages, editor extensions, separate icon NOTICE files | Not lightweight as a complete bundle; substantial build and platform surface | Prefer a bounded diff-review edition; preserve all root and nested notices; avoid redistributing unnecessary extensions |
| MarketMind AI | `psrane8/Market-Research-Agent@23f6d6e4e83d158fc8f5be25844c631fd07f7f0e` | 8-file Streamlit prototype; CrewAI/LangChain, Gemini Flash 1.5, Serper API; requires provider keys | Lightweight prototype but dated model/provider assumptions and thin quality controls | Rebuild workflow with current provider abstraction, citations, freshness labels and deterministic report schema |

## Findings that change the original plan

### 1. LeadScout source is not a generic business directory scraper

Its README describes finding Quora discussions and extracting user profiles with Firecrawl, then writing results to Google Sheets through Composio. This introduces personal-data and platform-terms risks, and the product depends on external services. JARVIS must not copy the profile-harvesting behavior as a default. The commercial MVP should discover company-level public information from explicitly permitted sources, store provenance, throttle requests, and support deletion.

### 2. MailForge is a tutorial, not a finished application

The README instructs the operator to implement `call_llm` and `search_web`. It is suitable as a small workflow reference, not as a finished buyer download. The JARVIS version must implement those adapters, provide a no-key sample mode, add evidence checks, and test the CSV workflow.

### 3. ContentFlip has a large local inference footprint

The source uses local speech recognition and documents a model download around 1GB. This conflicts with a blanket promise of lightweight/serverless operation. Split transcription into local optional runtime and a separately configured remote provider. Do not bundle model weights until their exact licenses and redistribution terms are cleared.

### 4. CodeSentinel has substantial license/asset surface

The repository contains over a thousand files, platform-specific packages, extensions, and nested NOTICE files. A full clone is not the right commercial package. Scope a small CLI/diff workflow and include only files required by the selected build, while preserving the applicable Apache-2.0 notices and auditing all included subcomponents.

### 5. DocuSense and SocialSync are feature-rich but service-heavy

DocuSense's complete architecture includes Next.js, FastAPI, LangGraph and Postgres/pgvector. SocialSync's documented setup requires multiple external service keys and LangGraph tooling. For low operating cost, JARVIS should ship single-user/local-first variants and make hosted/multi-user features optional.

## Preliminary architecture decisions

- **Default packaging:** local-first single-user edition with a simple setup command and explicit provider configuration.
- **Serverless option:** stateless API endpoints for short operations only; background jobs for long transcription, large PDF indexing, or multi-agent research.
- **Persistence:** SQLite/local files for the single-user edition; optional Postgres/pgvector only when multi-user scale justifies it.
- **LLM providers:** provider-neutral interface; model name, endpoint, timeout, and token budget configurable.
- **External data:** source adapter with rate limits, attribution, timestamp, terms link, and deletion/retention rules.
- **Human-in-the-loop:** required before email sending, social publishing, trade execution, legal reliance, or code modifications.
- **Cost controls:** token caps, max document size, concurrency limits, bounded retries, caching where allowed, and estimated cost display.

## Next technical gates

1. Fetch and inspect all direct dependency manifests and lockfiles at the pinned commit.
2. Generate a complete SPDX/CycloneDX dependency inventory per chosen product.
3. Review model and dataset license lineage; no model download is assumed commercially redistributable.
4. Inspect code paths for secrets, telemetry, outbound requests, shell execution, upload handling, and unsafe deserialization.
5. Run upstream test suites and record baseline results.
6. Choose the smallest legally eligible subset to fork or adapt.
7. Create an original product implementation and tests before creating commercial ZIPs.

## License evidence

Top-level upstream license texts were fetched from the default branch for all ten sources on 2026-11-15. MIT was confirmed for products 01, 02, 04, 05, 06, 07, 08 and 10; Apache-2.0 was confirmed for products 03 and 09. This does not establish that every dependency, model, dataset, icon, bundled binary, or service used by the projects is MIT/Apache-2.0.
