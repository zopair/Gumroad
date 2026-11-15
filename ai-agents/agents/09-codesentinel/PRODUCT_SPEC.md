# CodeSentinel — Product Specification

**Product family:** JARVIS — Intelligent Business & Productivity Agents  
**Publisher:** Zubair Digital Kits  
**Status:** Foundation specification only; implementation and release are not complete.  
**Primary upstream candidate:** https://github.com/alibaba/open-code-review  
**Top-level upstream license checked:** Apache-2.0 (preliminary; see [source register](../../SOURCE_REGISTER.md)).

## Product outcome
Source-code review and security findings.

## Primary user workflow
Diff/archive → static checks → bounded AI review → consolidate line-level findings → report.

## MVP scope
Diff-first review; deterministic rules; supported-language matrix; severity/confidence; line references; textual patch suggestions.

## Explicit exclusions and safeguards
Do not execute untrusted code by default; no claim of complete vulnerability detection.

## Qualification work remaining
Source qualification: inspect NOTICE and transitive licenses, rule sources, shell execution, repository permissions, and sandboxing.

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
