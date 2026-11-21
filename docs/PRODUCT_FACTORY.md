# Product Factory — Operating Guide

This repository hosts the intake/control layer for the existing Gumroad, Amazon KDP, Happy Little Train, and RelayMind pipelines. It does not replace those engines.

## Current flow

`idea → manifest → existing production pipeline → quality report → owner approval issue → owner-operated publishing → RelayMind promotion`

- Intake is manual via **Product Factory — Intake**.
- A validated manifest is committed under `manifests/<slug>.json`.
- Each version gets a GitHub issue containing the exact version fingerprint and a review checklist.
- No workflow publishes to Gumroad or KDP. The owner performs the final browser session and Print Previewer review.
- RelayMind remains a separate promotion engine; rendering is started manually after a product is actually published.

## Existing engine boundaries

| Channel | Source engine | Current boundary |
|---|---|---|
| `gumroad-kit` | [Gumroad](https://github.com/zopair/Gumroad) | Produces guide, CSV, XLSX and visual assets. Listing edits remain browser/manual. |
| `kdp-paperback` | [Amazon](https://github.com/zopair/Amazon) | Existing deterministic build and preflight. Human artwork review and KDP Print Previewer remain mandatory. |
| `kdp-kindle` | Amazon / future EPUB pipeline | Not yet verified as implemented; do not mark produced until EPUBCheck passes. |
| Happy Little Train | [Amazon-work-](https://github.com/zopair/Amazon-work-) | Separate 24-illustration dependency; not automatically dispatched. |
| Promotion | [RelayMind Core](https://github.com/zopair/relaymind-core) | Manual workflow; optional best-effort providers and bounded runner. |

## Approval and release policy

- A manifest starts as `draft`.
- Production changes it to `produced` only after its channel-specific quality gates pass and reports are attached.
- The owner must review the exact manifest version and apply `approved-to-publish` to its issue.
- Approval does not equal publishing. Publishing is a separate owner-operated browser session.
- Never add approval labels automatically, infer approval from comments, or retry failed jobs indefinitely.
- A changed product-defining input changes `version_sha256` and requires a new approval issue.

## Known blockers (verified 2026-11-21)

1. Amazon PR #6 has composition changes but requires owner visual-direction review; its Fruit Friends quality audit remains a human-review gate.
2. Amazon issue #7/#8 record a conflicting occupancy target: machine JSON 20–50%, prose specification 45–70%. Do not change thresholds without owner direction.
3. Amazon PR #9 fixes missing dependency installation in the inspector workflow, but its full suite still reports the two Fruit Friends composition failures.
4. Happy Little Train still requires 24 original illustrations at the repository's stated minimum dimensions.
5. Gumroad's ten published product slots are already occupied. New products must remain drafts unless a slot is freed.
6. The Kindle EPUB production/EPUBCheck path is not confirmed by the currently inspected repository README.

## Cost and licensing

Default execution is GitHub Actions/manual and existing browser engines. No paid API, new hosted service, or new runtime dependency is introduced by the intake layer. Artwork, fonts, voices, music, and other media still require source-specific rights checks.

## Tests

`python -m unittest discover -s tests -p 'test_product_factory.py' -v`

## Intellectual Property & Authorship

Copyright © Aly Hussein Zopair (علي حسين زبير ALY HUSSEIN ZOPAIR). All rights reserved unless a separate license or written agreement states otherwise.
