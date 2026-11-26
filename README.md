# RelayMind — idea → vertical video, $0/month

RelayMind turns a one-line idea (English or Arabic) into a **1080×1920 MP4 short** with a script, voice-over (English), Ken Burns visuals, kinetic captions and a procedural music bed. The default engine, **RelayMind Studio**, runs **100% inside the visitor's browser**: no server, no shared API key, and no GitHub compute on the owner's account.

## Studio engine (default, in-browser)

| Layer | Primary (free) | Fallbacks |
|---|---|---|
| Script | Client's **own** free Google AI Studio key (Gemini, optional) | Wikipedia facts in EN/AR (CC BY-SA, credited) → local templates |
| Visuals | Openverse (commercial + modification licences only) | Wikimedia Commons (no NC/ND) → procedural gradient art |
| Voice | Kokoro-82M ONNX via `kokoro-js` 1.2.1 (Apache-2.0), runs locally, ~90 MB first download then cached | captions only. **Arabic = captions + music** (no licence-safe in-browser Arabic voice yet) |
| Music | Procedural chord pad + bass, synthesised with Web Audio, auto-ducked under the voice | — |
| Encode | WebCodecs H.264 High (`avc1.640028`) + AAC, or Opus where AAC is unavailable, muxed by `mp4-muxer` (MIT) | VP9 → MediaRecorder real-time capture |
| Delivery | In-app player + MP4 download, Telegram `sendVideo` sent straight from the browser | WhatsApp share sheet / `wa.me` |

Every API call is made from the visitor's own IP with per-render caching and a circuit breaker (429/5xx → skip that source), so one viewer can't exhaust a shared quota and the owner pays nothing. Measured in headless Chromium: 540×960 demo ≈ 6–12 s; 1080×1920 Arabic ≈ 19 s; 1080×1920 English with voice ≈ 95 s on first run (includes the one-time model download).

Demo (no licence) = 540×960, watermark, no voice. Pro (licence key) = 1080×1920 + voice + Telegram.

## Hosting (Google Sites)

1. Google Sites → **Insert → Embed → Embed code** → paste the contents of [`embed/google-sites.html`](embed/google-sites.html) → Insert → stretch the box to full width, ~900 px tall → Publish.
2. The loader pulls `index.html` from jsDelivr pinned to the **v1** tag (`@1`), so a broken commit on `main` never reaches customers. Release = push to `main`, then tag `v1.x.y`.
3. Google Sites' embed sandbox allows scripts, storage, pop-ups and downloads, which is everything the app needs.

## Why not GitHub Pages / Actions for customers

GitHub's [Additional Product Terms](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features) forbid using Actions to provide a commercial stand-alone or integrated service, or as part of a serverless application, and forbid using Pages to run commercial SaaS. The owner account therefore runs only `relaymind-selftest.yml`, which tests this software project and is allowed. The GitHub render path is kept as an **optional advanced mode**: each customer connects their own account in Setup steps 1–3 and ticks "Render on my GitHub". It is off by default.

## Optional GitHub mode (server-side Python engine)

| Layer | Primary (free) | Fallbacks |
|---|---|---|
| Script | Pollinations text API (keyless server-side) | `LLM_BASE_URL` → local templates |
| Voice | `edge-tts` 7.3.1 (`en-US-AriaNeural`, `ar-EG-SalmaNeural`) | gTTS → espeak-ng → pyttsx3 → silence |
| Visuals | Pollinations image (1 / 45 s / IP) | Openverse → Wikimedia → procedural |
| Video | FFmpeg + Pillow, EBU R128 loudnorm −14 LUFS | — |

Client workflow: `workflow_dispatch` only (no cron), `concurrency: relaymind-render` with cancel-in-progress, `timeout-minutes: 4`, pip cache, engine fetched from jsDelivr `@1` (→ fastly → raw `main`), artifacts kept 3 days.

## Files

| Path | Purpose |
|---|---|
| `index.html` | Single-file app: chat UI, setup drawer, EN/AR RTL, dark mode, 4-layer settings persistence, **Studio engine** (`<script type="module" id="relaymindStudio">`) |
| `embed/google-sites.html` | Paste-in loader for Google Sites |
| `runner.py`, `engine/*.py`, `requirements.txt` | Server-side engine for the optional GitHub mode and self-tests |
| `templates/client_workflow.yml` | Workflow installed in a customer's own repo (GitHub mode only) |
| `.github/workflows/relaymind-selftest.yml` | Owner-side manual test of the Python engine |
| `scripts/sync_relaymind_template.py` | Re-embeds the workflow template inside `index.html` |

## Owner checklist

- Change the licence key: put the SHA-256 of the new key in `LICENSE_SHA256` inside `index.html`, then commit and tag a new `v1.x.y`.
- Local test: `python -m http.server` in the repo, then open `http://localhost:8000/`. Python engine: `python runner.py --dry-run --out /tmp/dry`.

## Limits to know

- The licence check is client-side (hash compare), so it deters casual copying but is not tamper-proof.
- Kokoro voice: ~90 MB on first use, so phones on mobile data should use Wi-Fi. Fastest on desktop Chrome/Edge; Safari 17+ supported.
- Videos encoded with Opus audio (Chromium on Linux) play in browsers and on Telegram. Some older iOS players need AAC, which Windows, macOS, Android and iOS browsers produce automatically.
- Openverse and Wikimedia images keep their CC licence. Credits are shown under every video under **Credits**.
- Pollinations now requires a Cloudflare Turnstile token for browser calls, so the Studio engine doesn't use it.

---

# Zubair Digital Kits

A curated catalog of ten published digital workbooks and templates for Gumroad.

- Storefront: https://zopair.gumroad.com
- Live catalog and product source files: [CATALOG.md](CATALOG.md)
- Current Gumroad metadata and policies: [STORE_SETUP.md](STORE_SETUP.md)
- **Publishing, file delivery, image specifications, deployment limits and free/open-source tools:** [docs/PUBLISHING_AND_ASSET_STANDARDS.md](docs/PUBLISHING_AND_ASSET_STANDARDS.md)
- Competitor research and growth plan: [GROWTH_PLAYBOOK.md](GROWTH_PLAYBOOK.md)
- **Competitor benchmark and simple-product strategy:** [research/COMPETITOR_BENCHMARK.md](research/COMPETITOR_BENCHMARK.md)
- Prepared custom storefront page: [storefront/profile.html](storefront/profile.html)
- Free samples: [samples/](samples/)
- Organic campaign: [30-day launch plan](marketing/30-day-launch-plan.md), [Pinterest copy](marketing/pinterest/pin-copy.md), [vertical pins](marketing/pinterest/)
- Brand identity: [storefront assets](storefront/)
- Product workbooks: generated and tested through [build-product-workbooks.yml](.github/workflows/build-product-workbooks.yml)
- Product image gallery and mockups: generated through [render-product-covers.yml](.github/workflows/render-product-covers.yml)

Each live product includes an editable Markdown guide, a matching CSV worksheet and an XLSX workbook. Product-specific preview images and mockups are stored under each product folder.

The ten product slots are occupied. Additional catalog ideas are internal backlog only. All product materials must remain original or appropriately licensed, and each listing must accurately describe its actual files and limitations.

## Quality gates

- Run workbook regression tests before changing workbook generation.
- Verify every Gumroad attachment matches its source file.
- Keep product title, summary, tags, description and preview aligned with included deliverables.
- Do not claim sales, rankings, reviews or guaranteed outcomes without verified evidence.
- Do not publish new products unless a published slot becomes available or the account limit changes.
- Follow [Publishing & Asset Standards](docs/PUBLISHING_AND_ASSET_STANDARDS.md) for provider limits, file/image formats, deployment routes, and release checks.


## Technical Setup & Verification

The repository contains two distinct tracks: the Zubair Digital Kits product catalog/workbook generator and the optional RelayMind video studio. They have separate workflows and runtime requirements.

### Product workbook and asset checks

```bash
python -m pip install -r requirements.txt openpyxl
python -m unittest discover -s tests -v
python scripts/build_product_workbooks.py . dist
python scripts/validate_gumroad_assets.py
```

The workbook test suite verifies ten generated XLSX workbooks, selected formulas, data validation, and content counts. The asset validator checks PNG dimensions, DPI metadata, file size, and thumbnail geometry. The cover-render workflow also requires the system `librsvg2-bin` package.

### RelayMind local dry run

```bash
python -m pip install -r requirements.txt
python runner.py --dry-run --out /tmp/relaymind-dry-run
```

The default browser Studio and optional GitHub/Actions render mode are separate execution paths. Any external provider key, model download, or service quota must be evaluated independently; the repository does not guarantee unlimited free external inference.

### Automation write boundary

The workbook and product-cover workflows currently request `contents: write` and commit generated workbooks/assets directly to `main` after their checks. They do not open a review PR. The RelayMind owner self-test is manual and read-only. Review generated files and workflow permissions before enabling additional automation.

## Proof of Concept & Enterprise Customization Readiness

**Status: Product catalog with generated digital deliverables plus a separate browser-first video-studio PoC.** The repository includes ten editable XLSX workbooks with regression tests, product previews and marketing assets, and an optional video generation engine. It does not establish external marketplace sales, customer outcomes, or that every product brief is already published as a Gumroad listing.

| Area | Current state / boundary |
|---|---|
| Digital product workbooks | Ten generated XLSX deliverables; selected content/formula regression tests |
| Product visual assets | SVG source and rendered PNG/GIF previews; image-size/DPI validator |
| Catalog and storefront | Static product catalog and profile page; Gumroad transaction state is external |
| RelayMind browser Studio | Client-side generation flow; visitor supplies their own optional API key; fallback sources and local rendering have separate terms/limits |
| RelayMind GitHub mode | Optional customer-owned workflow path; not the default owner-side hosting model |
| Voice / media dependencies | Edge-TTS, gTTS, FFmpeg/Pillow and browser ONNX model; review each upstream license and network requirement |
| Test coverage | Workbook and image asset tests; manual RelayMind self-test workflow |
| Direct workflow writes | Workbook and cover workflows can push generated artifacts directly to main |
| Software license | `LICENSE.md` defines customer usage terms for Zubair Digital Kits products; it is not a general open-source license for all repository source code |

### Readiness gates

1. Verify each Gumroad listing's actual published status, price, files, preview, and license terms in the Gumroad account; repository files alone do not prove publication.
2. Keep the workbook source, generated workbook, CSV companion, preview images, and listing description synchronized.
3. Add `openpyxl` explicitly to the documented development/test dependency set or a dedicated dev requirements file.
4. Review direct-to-main workflow permissions and consider PR-based artifact updates if owner review is required.
5. Maintain per-asset third-party license attribution for fonts, images, voices, models, and generated media.
6. Do not claim unlimited free AI usage; external keys, quota limits, browser APIs, and model downloads remain subject to provider terms.
7. Keep RelayMind's client-side licensing check described as a deterrent, not tamper-proof access control.

## Intellectual Property & Authorship

Project authorship and attribution: **Aly Hussein Zopair (علي حسين زبير ALY HUSSEIN ZOPAIR)**.

The product-use terms in `LICENSE.md` apply to Zubair Digital Kits deliverables as written. They do not automatically grant an open-source license to all source code or third-party components in this repository. Review and clarify the intended code license before redistribution.
