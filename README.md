# RelayMind — idea → vertical video, $0/month

RelayMind turns a one-line idea (English or Arabic) into a **1080×1920 MP4 short** with an AI-written script, neural voice-over, Ken Burns visuals, burned-in kinetic captions and loudness-normalised audio. Everything runs on **free infrastructure**: each client's own GitHub Actions minutes, keyless open APIs, and local fallbacks so a render never fails.

| Layer | Primary (free) | Fallbacks |
|---|---|---|
| Script writer | Pollinations text API (keyless, OpenAI-compatible) | optional `LLM_BASE_URL` endpoint → GitHub Models (retired 2026-07-30, quick last try) → deterministic local templates |
| Voice | `edge-tts` 7.3.1 (`en-US-AriaNeural`, `ar-EG-SalmaNeural`, …) | second Edge voice → gTTS → espeak-ng → pyttsx3 → timed silence |
| Visuals | Pollinations image (rate-aware: 1 / 45 s / IP) | Openverse (CC, commercial + modification licences only) → Wikimedia Commons → procedural gradient art |
| Video | FFmpeg (system or bundled `imageio-ffmpeg`) + Pillow | — |
| Delivery | In-app player + MP4 download | Telegram `sendVideo` → `sendDocument` → text notice; WhatsApp share sheet |

## Files

| Path | Purpose |
|---|---|
| `index.html` | Single-file web app (GitHub Pages + Google Sites iframe). Chat UI, setup drawer, EN/AR, dark mode, demo mode, in-app render + player |
| `runner.py` | Orchestrator. Env: `TOPIC`, `LANG_CODE` (or `LANG`), `VOICE`, `GITHUB_TOKEN`, `TG_TOKEN`, `TG_CHAT_ID`, `POLLINATIONS_TOKEN` (optional) |
| `engine/prompt_enhancer.py` | Silent viral-script + 9:16 visual-prompt generator with local fallback |
| `engine/media_factory.py` | TTS chain, visual chain, captions, Ken Burns scenes, concat, EBU R128 loudnorm → `output/final_short.mp4` |
| `engine/resolver.py` | Retry/backoff, provider rotation, circuit breakers, health checks, GitHub repo discovery, Telegram upload |
| `templates/client_workflow.yml` | Minute-saving workflow injected into each client repo as `.github/workflows/relaymind.yml` |
| `.github/workflows/relaymind-selftest.yml` | Owner-side manual self-test (dry run + full render) |
| `scripts/sync_relaymind_template.py` | Re-embeds the workflow template inside `index.html` (offline fallback copy) |

## How a render works

1. The client opens the web app, enters the license key, pastes their GitHub link and a classic token (`repo`, `workflow` scopes) and presses **Enter**.
2. The app creates `relaymind-studio` (private) if needed, writes `README.md` first when the repo is empty, installs `.github/workflows/relaymind.yml`, saves `relaymind.config.json`, and checks every call for HTTP 200/201.
3. Optional: Telegram bot token + chat ID are encrypted in the browser (libsodium sealed box) and stored as **repository secrets**.
4. Each idea is enhanced in the browser (keyless Pollinations), the default branch is detected, the workflow is dispatched with a unique `request_id`, and the run is polled every 8 s.
5. The MP4 is pulled from the run artifact (JSZip, in-browser) or, if the artifact download is blocked by CORS, from the `relaymind-renders` branch through the GitHub contents API. The user never leaves the chat.

Client workflow guarantees: `workflow_dispatch` only (no cron), `concurrency: relaymind-render` with cancel-in-progress, `timeout-minutes: 4`, pip cache via `actions/setup-python@v7`, engine fetched from **jsDelivr** (`cdn.jsdelivr.net` → `fastly.jsdelivr.net` → raw fallback), artifacts kept 3 days. A typical 35–45 s video takes ~65 s of runner time end to end.

## Owner checklist

1. **Make this repository public** (or move the engine files to a public repo and change `ENGINE_REPO` in `templates/client_workflow.yml` and `index.html`). jsDelivr only serves public repos, and GitHub Pages on a Free plan needs a public repo.
2. Enable Pages: Settings → Pages → Deploy from branch → `main` / root. The app is then at `https://zopair.github.io/Gumroad/`.
3. Google Sites: Insert → Embed → By URL → paste the Pages URL.
4. After pushing engine changes, refresh the CDN: `https://purge.jsdelivr.net/gh/zopair/Gumroad@main/engine/media_factory.py` (one URL per changed file), or pin `ENGINE_REF` to a tag.
5. Change the license key: put the SHA-256 of the new key in `LICENSE_SHA256` inside `index.html`.

## Local test

```bash
pip install -r requirements.txt
python runner.py --dry-run --out /tmp/dry                      # offline, 3 scenes, local voice/visuals
TOPIC="Why octopuses are geniuses" LANG_CODE=en python runner.py
TOPIC="فوائد المشي اليومي" LANG_CODE=ar python runner.py
```

`output/report.json` records which provider served every scene, image credits (CC licence + source URL), timings and any errors.

## Limits to know

- Free tiers change. Pollinations anonymous limits in Nov 2026: 1 image and 1 text reply per 45 s per IP. A free registered key (`POLLINATIONS_TOKEN` secret) removes the wait; without it the hook scene gets an AI image and the rest use Openverse/Wikimedia.
- Private client repos get 2,000 free Actions minutes/month on GitHub Free (~1,500 renders); public repos are unlimited on standard runners.
- The license check is client-side (hash compare). It deters casual use but is not tamper-proof; use a server-side check if you need real enforcement.
- Openverse images keep their CC licence (BY / BY-SA need attribution). Credits are saved in `report.json`.

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
