# MailForge Pro — Product Specification

**Product family:** JARVIS — Intelligent Business & Productivity Agents  
**Publisher:** Zubair Digital Kits  
**Status:** Foundation specification only; implementation and release are not complete.  
**Primary upstream candidate:** https://github.com/The-Pocket/PocketFlow-Tutorial-Cold-Email-Personalization  
**Top-level upstream license checked:** MIT (preliminary; see [source register](../../SOURCE_REGISTER.md)).

## Product outcome
Personalized B2B cold-email drafting.

## Primary user workflow
Prospect/company context → value proposition → evidence-backed personalization → email variants → review/export.

## MVP scope
Subject variants; 3-step sequence; personalization evidence; tone controls; merge fields; CSV export; anti-spam checklist.

## Explicit exclusions and safeguards
No bulk sending by default; no fabricated personalization or deliverability guarantees.

## Qualification work remaining
Source qualification: inspect scraping/enrichment sources, email data provenance, consent requirements, and all dependencies.

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
