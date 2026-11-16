# JARVIS AI Agents — Product Blueprints

All products use the JARVIS product-family identity with a distinct product-specific interface and visual concept. The first release of each product must prioritize one reliable end-to-end workflow over a broad collection of unverified features.

## Shared product promise

**JARVIS — Intelligent Business & Productivity Agents**  
A family of practical AI assistants designed to turn focused business tasks into repeatable workflows. Each product is independently installable, configurable, and documented.

## 01 — RankMaster AI

**Positioning:** Your SEO research and content optimization assistant.  
**Primary workflow:** Enter a website/topic and target audience → research keyword intent from a configured data source → create a content brief → draft/optimize content → export an actionable report.  
**MVP:** keyword/topic clustering from supplied data; search-intent labeling; outline generation; title/meta suggestions; on-page checklist; Markdown export.  
**Not promised:** guaranteed Google rankings, proprietary keyword-volume data without a licensed provider, automatic publishing.  
**Buyer:** creators, small agencies, website owners.  
**Visual concept:** dark navy editorial SEO workspace, gold ranking/intent indicators, clear content scorecards.

## 02 — LeadScout Bot

**Positioning:** Find, qualify, and organize business prospects from permitted public sources.  
**Primary workflow:** Define industry and geography → query approved data source → normalize and deduplicate records → qualify against user criteria → export CSV.  
**MVP:** provider adapter, source URL/provenance per record, deduplication, qualification rubric, CSV export, request throttling.  
**Not promised:** verified personal emails unless a compliant provider confirms them; bypassing platform restrictions; unrestricted scraping.  
**Buyer:** B2B founders, sales teams, agencies.  
**Visual concept:** premium prospect pipeline with source badges, qualification score and clean lead cards.

## 03 — TradeTrend Analyst

**Positioning:** Multi-perspective market research and trading-scenario analysis.  
**Primary workflow:** Select asset and timeframe → load permitted historical/current data → calculate indicators → run analyst perspectives → reconcile bull/base/bear cases → produce cited report.  
**MVP:** historical-data adapter, deterministic indicator calculations, news/source links, scenario analysis, paper-trading/backtest mode, risk disclosure.  
**Not promised:** profits, predictive certainty, financial advice, unattended live trading.  
**Buyer:** market researchers and experienced traders.  
**Visual concept:** restrained trading research terminal, graphite/navy canvas, gold signal markers, legible charts.

## 04 — DocuSense Support

**Positioning:** Ask questions across PDFs and receive answers grounded in page-level evidence.  
**Primary workflow:** Upload PDF → parse and chunk → index → ask question → retrieve evidence → answer with page citations and abstain when evidence is insufficient.  
**MVP:** multi-PDF ingestion, page-aware chunks, local persistent index, retrieval, cited answers, delete-document action, source preview.  
**Not promised:** perfect OCR or hallucination-free answers; confidential cloud processing without disclosure.  
**Buyer:** support teams, consultants, educators, operations teams.  
**Visual concept:** document library and chat workspace with highlighted citations and page preview.

## 05 — SocialSync AI

**Positioning:** Plan, draft, adapt, and approve social content in one workflow.  
**Primary workflow:** Configure brand voice → generate channel-specific drafts → preview → human approval → export/schedule through authorized integration.  
**MVP:** content calendar, channel templates, tone rules, approval states, exportable post pack; publishing integration is optional and separately configured.  
**Not promised:** guaranteed reach/engagement or unrestricted auto-posting.  
**Buyer:** creators, marketing teams, small businesses.  
**Visual concept:** editorial calendar, channel previews, approval queue, strong platform-specific previews.

## 06 — MailForge Pro

**Positioning:** Write researched, relevant, personalized B2B outreach—without sending blindly.  
**Primary workflow:** Enter prospect/company context → define value proposition → generate subject/body variants → review personalization evidence → approve/export sequence.  
**MVP:** email brief, personalization fields with source notes, 3-step sequence, subject variants, tone controls, CSV merge export, compliance checklist.  
**Not promised:** guaranteed deliverability or automatic bulk sending.  
**Buyer:** founders, consultants, B2B sales teams.  
**Visual concept:** polished email editor, personalization tokens, sequence timeline, preview pane.

## 07 — ContentFlip AI

**Positioning:** Turn authorized video/audio into structured, reusable written content.  
**Primary workflow:** Upload local media or provide an authorized source → transcribe → review transcript → choose article template → generate draft → export Markdown/HTML.  
**MVP:** local file input, transcript editor, timestamps/source metadata, article templates, editable output, attribution reminder.  
**Not promised:** unrestricted downloads from third-party platforms or rights to republish content.  
**Buyer:** educators, creators, podcasters, marketers.  
**Visual concept:** media timeline flowing into a premium article editor with source provenance.

## 08 — EstateGuard AI

**Positioning:** Understand contract structure and identify clauses that deserve professional review.  
**Primary workflow:** Upload contract → extract text and clauses → classify obligations/dates/risks → link every finding to source text/page → export review checklist.  
**MVP:** PDF/DOCX ingestion, clause extraction, risk taxonomy, evidence references, uncertainty labels, review report.  
**Not promised:** legal advice, enforceability conclusions, or jurisdictional coverage without qualified validation.  
**Buyer:** property managers, investors, administrators, legal operations.  
**Visual concept:** contract review desk, highlighted clause references, severity-coded findings, clean legal typography.

## 09 — CodeSentinel

**Positioning:** Catch code-quality and security issues before merge.  
**Primary workflow:** Select a diff or upload source archive → parse changed files → run deterministic checks → request bounded AI review → consolidate findings with file/line references → export review.  
**MVP:** diff-first review, supported language declaration, rule-based checks, AI explanation, severity/confidence, patch suggestions as text only.  
**Not promised:** complete vulnerability detection or safe execution of arbitrary repository code.  
**Buyer:** developers, maintainers, small engineering teams.  
**Visual concept:** code review console, precise line annotations, severity filters, secure-by-default status.

## 10 — MarketMind AI

**Positioning:** Turn market and competitor research into a structured decision brief.  
**Primary workflow:** Define market and competitor set → gather source-linked evidence → compare positioning/offers/pricing → identify gaps → produce SWOT and executive brief.  
**MVP:** user-defined competitor list, approved search/data connectors, evidence ledger, comparison matrix, SWOT, dated report export.  
**Not promised:** complete market coverage, real-time price accuracy without a provider, unsupported market-size claims.  
**Buyer:** founders, consultants, product marketers, small businesses.  
**Visual concept:** executive intelligence dashboard, competitor matrix, source-backed insights, premium report cover.

## Shared UX acceptance criteria

- Responsive layout; accessible contrast and keyboard navigation.
- Clear empty/loading/error/success states.
- API key setup wizard and connection test.
- User-visible provider/cost disclosure before paid calls.
- No hidden outbound calls or telemetry.
- Export and delete controls where user data is stored.
- Sample/demo mode that works without real credentials where technically feasible.
- Every AI-generated finding is distinguishable from verified source data.
