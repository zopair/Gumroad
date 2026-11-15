# JARVIS AI Agents — Zubair Digital Kits

> Internal product-development program. These are not published Gumroad products and are not yet release-ready.

**Publisher:** Zubair Digital Kits  
**Product family:** JARVIS — Intelligent Business & Productivity Agents  
**Branch:** `feat/jarvis-ai-agents-foundation`  
**Baseline reviewed:** 2026-11-15

## Mission

Build ten independent, commercially distributable AI-agent products from carefully selected open-source foundations. Each product must deliver a working, testable user outcome—not merely a renamed repository, prompt pack, or mock interface.

## Non-negotiable release gates

1. The selected primary upstream repository must have an explicit MIT or Apache-2.0 license.
2. Review the exact upstream commit, complete source tree, dependency licenses, model licenses, datasets, fonts, icons, and bundled assets.
3. Preserve required copyright, license, NOTICE, and attribution text. Never remove upstream legal notices when white-labeling UI.
4. Add original JARVIS product identity only in the product presentation layer.
5. Ship a reproducible build, setup guide, sample data, tests, security notes, privacy notes, and a truthful feature/limitation list.
6. No embedded API keys, tokens, cookies, customer data, or developer credentials.
7. No live sending, posting, trading, scraping behind authentication, or destructive code changes without explicit end-user approval.
8. Do not claim serverless, offline, free, real-time, or production-ready behavior unless verified by tests and deployment evidence.
9. Build each product in its own directory and release ZIP. No cross-product runtime dependency unless documented and justified.
10. Gumroad publishing is a separate approval step. Do not publish or change any live product without the owner's explicit instruction.

## Product roster

| # | Product | Slug | Primary capability |
|---:|---|---|---|
| 01 | RankMaster AI | `rankmaster-ai` | SEO research and content optimization |
| 02 | LeadScout Bot | `leadscout-bot` | Public business lead discovery and qualification |
| 03 | TradeTrend Analyst | `tradetrend-analyst` | Market research and simulated multi-agent analysis |
| 04 | DocuSense Support | `docusense-support` | PDF knowledge assistant with cited RAG answers |
| 05 | SocialSync AI | `socialsync-ai` | Social content planning and approval workflow |
| 06 | MailForge Pro | `mailforge-pro` | Personalized cold-email drafting |
| 07 | ContentFlip AI | `contentflip-ai` | Authorized video/audio transcription to articles |
| 08 | EstateGuard AI | `estateguard-ai` | Contract clause extraction and risk triage |
| 09 | CodeSentinel | `codesentinel` | Source-code review and security findings |
| 10 | MarketMind AI | `marketmind-ai` | Market and competitor research reports |

## Repository navigation

- [Source register and license gate](SOURCE_REGISTER.md)
- [Product blueprints and acceptance criteria](PRODUCT_BLUEPRINTS.md)
- [Brand and white-labeling standard](BRAND_SYSTEM.md)
- [Packaging, security, and legal release gates](PACKAGING_AND_LEGAL.md)

## Delivery stages

- **Stage 0 — Foundation:** product roster, architecture, source candidates, license evidence, release gates.
- **Stage 1 — Source qualification:** pin commits; inspect dependency trees and licenses; run source tests; threat-model.
- **Stage 2 — Product implementation:** fork/adapt only qualified code; implement product-specific UX and workflows.
- **Stage 3 — Validation:** unit/integration/security/packaging tests and clean-machine installation.
- **Stage 4 — Commercial assets:** original cover, thumbnail, screenshots, demo, listing copy, ZIP and changelog.
- **Stage 5 — Owner approval:** review final product and approve Gumroad listing/publishing.

## Current status

Stage 0 is being established. The upstream LICENSE files for the ten candidate repositories were checked at their default branch heads on 2026-11-15. This is **not** a complete license audit: dependencies, model weights, datasets, assets, exact pinned commits, and current runtime behavior remain to be reviewed before any source is approved for redistribution.
