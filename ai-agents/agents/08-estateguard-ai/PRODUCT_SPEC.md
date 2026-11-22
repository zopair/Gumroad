# EstateGuard AI — Product Specification

**Product family:** JARVIS — Intelligent Business & Productivity Agents  
**Publisher:** Zubair Digital Kits  
**Status:** Foundation specification only; implementation and release are not complete.  
**Primary upstream candidate:** https://github.com/gautampapat/Smart-PDF-Contract-Analyzer  
**Top-level upstream license checked:** MIT (preliminary; see [source register](../../SOURCE_REGISTER.md)).

## Current implementation snapshot — 2026-11-15
The current local workflow scans supplied contract text using 14 transparent clause-category rules, returns line-level evidence and review prompts, and flags selected high-impact phrases for priority review. It does not yet parse PDF/DOCX files, perform OCR, extract structured obligations/dates, or provide jurisdiction-specific legal analysis.

## Product outcome
Contract clause extraction and risk triage.

## Primary user workflow
PDF/DOCX → text extraction → clause classification → source-linked risk findings → review checklist.

## MVP scope
Clause extraction; obligations/dates; severity and confidence; evidence snippets/page references; report export; human review.

## Explicit exclusions and safeguards
Not legal advice; no enforceability conclusions or jurisdiction claims without qualified legal review.

## Qualification work remaining
Source qualification: inspect datasets/model lineage, OCR, legal taxonomy, privacy, and jurisdiction coverage.

## Architecture principles
- Small, separable modules; provider adapters behind interfaces.
- On-demand execution first; no always-on service unless the use case proves it necessary.
- Local storage by default for single-user workflows where feasible.
- Secrets supplied by the buyer at runtime; never embedded in source or sample files.
- Deterministic fixture mode for repeatable tests and product demos.
- Explicit consent before external actions or transmission of sensitive user content.

## Definition of done
- [ ] Exact upstream commit pinned and source tree reviewed.
- [ ] Full dependency, model, dataset, and asset license audit approved.
- [ ] Build and install verified from a clean environment.
- [ ] Core workflow has unit and integration tests.
- [ ] Failure, rate-limit, invalid-input, and missing-credential paths tested.
- [ ] Security and privacy review completed.
- [ ] Original JARVIS UI and product-specific assets implemented.
- [ ] LICENSE, NOTICE, ATTRIBUTION, and third-party license inventory packaged.
- [ ] ZIP manifest, checksum, user guide, and real screenshots verified.
- [ ] Gumroad listing reviewed and explicitly approved by the owner.
