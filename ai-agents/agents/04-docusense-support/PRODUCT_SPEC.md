# DocuSense Support — Product Specification

**Product family:** JARVIS — Intelligent Business & Productivity Agents  
**Publisher:** Zubair Digital Kits  
**Status:** Foundation specification only; implementation and release are not complete.  
**Primary upstream candidate:** https://github.com/LeonAchata/DocuChat-AI  
**Top-level upstream license checked:** MIT (preliminary; see [source register](../../SOURCE_REGISTER.md)).

## Product outcome
PDF knowledge assistant with page-cited RAG.

## Primary user workflow
PDF upload → parse/chunk/index → question → retrieve evidence → cited answer or abstention.

## MVP scope
Multi-PDF ingestion; page-aware citations; persistent local index; hybrid retrieval; document deletion; evidence preview.

## Explicit exclusions and safeguards
No claim of perfect accuracy or confidentiality if an external LLM receives document excerpts.

## Qualification work remaining
Source qualification: inspect PDF parser, OCR/model licenses, retention, prompt-injection defenses, and local deployment.

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
