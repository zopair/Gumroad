# JARVIS AI Agents — Upstream Source & License Register

**Review date:** 2026-11-15  
**Rule:** only MIT or Apache-2.0 primary project licenses are eligible. A top-level LICENSE check is preliminary evidence, not final legal clearance.

| # | Product | Candidate upstream | Branch | LICENSE evidence | Qualification status |
|---:|---|---|---|---|---|
| 01 | RankMaster AI | https://github.com/humanswith-ai/contentos-agent-lite | main | MIT text fetched from upstream LICENSE | Preliminary pass; inspect skills, data sources, and all bundled assets |
| 02 | LeadScout Bot | https://github.com/GURPREETKAURJETHRA/AI-Lead-Generation-Agent | main | MIT text fetched from upstream LICENSE | Preliminary pass; inspect scraping method, source terms, privacy, and data provenance |
| 03 | TradeTrend Analyst | https://github.com/TauricResearch/TradingAgents | main | Apache-2.0 text fetched from upstream LICENSE | Preliminary pass; inspect market-data terms, dependencies, model providers, and risk controls |
| 04 | DocuSense Support | https://github.com/LeonAchata/DocuChat-AI | main | MIT text fetched from upstream LICENSE | Preliminary pass; inspect OCR/parser/model dependencies and document retention |
| 05 | SocialSync AI | https://github.com/langchain-ai/social-media-agent | main | MIT text fetched from upstream LICENSE | Preliminary pass; inspect platform APIs, credentials, scheduling, and provider terms |
| 06 | MailForge Pro | https://github.com/The-Pocket/PocketFlow-Tutorial-Cold-Email-Personalization | master | MIT text fetched from upstream LICENSE | Preliminary pass; inspect enrichment sources, email data handling, and anti-spam safeguards |
| 07 | ContentFlip AI | https://github.com/DEKVIW/video-to-article | main | MIT text fetched from upstream LICENSE | Preliminary pass; inspect FFmpeg/ASR/model licenses and video platform terms |
| 08 | EstateGuard AI | https://github.com/gautampapat/Smart-PDF-Contract-Analyzer | main | MIT text fetched from upstream LICENSE | Preliminary pass; inspect CUAD/data/model lineage, legal claims, and jurisdiction limitations |
| 09 | CodeSentinel | https://github.com/alibaba/open-code-review | main | Apache-2.0 text fetched from upstream LICENSE | Preliminary pass; inspect NOTICE, rulesets, analyzers, and execution sandbox |
| 10 | MarketMind AI | https://github.com/psrane8/Market-Research-Agent | main | MIT text fetched from upstream LICENSE | Preliminary pass; inspect search/data provider terms, dependency licenses, and evidence citations |

## Required evidence before a source is approved

For each source, create a dated audit record containing:

- Canonical repository URL, owner, default branch, exact commit SHA, release/tag (if any), and retrieval date.
- Full upstream LICENSE text and all NOTICE/copyright files.
- Complete dependency inventory (direct and transitive) with SPDX identifiers and source URLs.
- Model/weight licenses, dataset licenses, prompt/template provenance, fonts, icons, images, and other non-code assets.
- Whether any dependency is AGPL/GPL, SSPL, BUSL, Commons Clause, non-commercial, source-available, or otherwise incompatible with the intended distribution model.
- Build and test evidence from the pinned commit.
- Security review: secrets, telemetry, outbound requests, file access, shell execution, browser automation, scraping, and unsafe deserialization.
- Product-specific compliance review (privacy, anti-spam, financial, legal, platform terms).
- Final disposition: `APPROVED`, `REJECTED`, or `REPLACE_SOURCE`, signed off internally.

## Important interpretation

A repository's MIT/Apache-2.0 license does not relicense its dependencies, model weights, training datasets, external services, or third-party assets. Do not remove author notices or misrepresent authorship. Preserve upstream license texts in each distributed package and add a separate JARVIS modification notice.

## Candidate selection caveats

- LeadScout must not rely on bypassing login, CAPTCHA, paywalls, rate limits, or platform access controls. Prefer licensed APIs and openly published business information.
- SocialSync must use authorized platform APIs and explicit account-owner approval. Browser automation must not be marketed as guaranteed or platform-approved.
- TradeTrend is an analytical/simulation product; no autonomous order execution in the first commercial release.
- EstateGuard is document triage, not legal advice or jurisdiction-specific legal representation.
- ContentFlip must process user-owned, licensed, or otherwise authorized media only.
- CodeSentinel must isolate untrusted repository code and never run arbitrary code on the host by default.
