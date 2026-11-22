# LeadScout Bot — Product Specification

**Product family:** JARVIS — Intelligent Business & Productivity Agents  
**Publisher:** Zubair Digital Kits  
**Status:** Foundation specification only; implementation and release are not complete.  
**Primary upstream candidate:** https://github.com/GURPREETKAURJETHRA/AI-Lead-Generation-Agent  
**Top-level upstream license checked:** MIT (preliminary; see [source register](../../SOURCE_REGISTER.md)).

## Product outcome
Public business lead discovery and qualification.

## Primary user workflow
Industry/geography criteria → approved public data provider → normalize/deduplicate → qualify → CSV export.

## MVP scope
Provider adapter; source URL and timestamp; company-level records; deduplication; qualification rubric; CSV export; rate limiting.

## Explicit exclusions and safeguards
No login bypass, CAPTCHA bypass, paywall access, prohibited scraping, or unverified personal-email claims.

## Qualification work remaining
Source qualification: inspect scraping implementation, target-site terms, PII handling, data provenance, and API alternatives.

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
