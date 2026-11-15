# Publishing, File Delivery & Asset Standards

**Store:** Zubair Digital Kits  
**Repository:** https://github.com/zopair/Gumroad  
**Store:** https://zopair.gumroad.com  
**Last verified:** 2026-11-15

This document is the operating contract for publishing, product delivery, storefront pages, images, and build tooling. Treat provider limits as hard ceilings, not targets. Recheck linked provider documentation before changing a pipeline because platform limits can change.

## 1. Publishing architecture

### 1.1 Source of truth

- GitHub is the source repository for editable source files, product source materials, artwork, build scripts, tests, and release documentation.
- Gumroad is the source of truth for published products, checkout, payment, buyer receipts, and paid file delivery.
- Never treat a GitHub-hosted file, external marketing page, or public image URL as a replacement for Gumroad's protected product delivery.
- Keep every purchase CTA pointed at the canonical Gumroad product URL. Do not embed or imitate checkout/payment forms on an external static site.

### 1.2 Preferred profile publishing route

Gumroad's current Help Center documents custom profile pages and the Gumroad CLI:
- Preview before publishing: `gumroad pages preview`
- Publish the profile page: `gumroad pages push profile`
- A custom page replaces the entire profile page/sections layout. Back up the current profile source before replacing it.
- Gumroad's custom page can use `data-gumroad-follow` and `data-gumroad-follow-message` for the native follower form.
- Live catalogue/prices are served with the Gumroad profile page. A standalone external page must not invent or hard-code claims that prices are live; link to the product page instead.
- Do not link directly to downloadable files from a Gumroad custom page. Gumroad warns that browser downloads initiated from a custom page can be cancelled silently. Put buyer files in product content and link to the product.
- The Gumroad product connector currently exposes product metadata, covers, and delivery-file management, but not custom profile HTML publishing. Use the documented CLI/UI for profile publishing; do not pretend the product API published the profile.

Official guide: https://gumroad.com/help/article/124-your-gumroad-profile-page

### 1.3 External static-hosting fallback

Use an external host only for a separate marketing/catalogue page that links to Gumroad. Do not make it the payment or file-delivery system.

| Provider | Free-tier facts checked | Decision |
|---|---|---|
| GitHub Pages | GitHub says Pages must not be used as free hosting for an online business/e-commerce site primarily facilitating commercial transactions. | **Do not use for this commercial storefront.** Keep GitHub for source control and CI. |
| Netlify Free | Current pricing advertises $0 Free with 300 credits/month and a hard monthly limit; Netlify's Free-plan announcement explicitly permits commercial projects. When the limit is reached, the site can pause; no automatic recharge on Free. | Best documented external fallback if a separate hosted marketing site is needed. Verify current terms/credits before launch. |
| Cloudflare Pages Free | Up to 500 builds/month, one concurrent build, 20,000 files/site, 25 MiB maximum per individual asset, and 20-minute build timeout. | Strong static-hosting alternative; keep any file larger than 25 MiB out of Pages assets and use object storage if required. Confirm account terms before production use. |

Provider documentation:
- GitHub Pages limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- Netlify pricing: https://www.netlify.com/pricing/
- Netlify commercial-project statement: https://www.netlify.com/blog/introducing-netlify-free-plan/
- Cloudflare Pages limits: https://developers.cloudflare.com/pages/platform/limits/

**No external deployment is implied by this document.** Do not create a new hosting project, connect a domain, or publish a replacement storefront without checking the existing account/project and confirming the final public page.

## 2. Gumroad product files

### 2.1 Current live delivery audit

All ten published products were checked through the Gumroad product/file endpoints on 2026-11-15:
- 10 published products.
- 3 delivered files per product; 30 attachments total.
- File types: Markdown (`MD`), CSV (`CSV`), and Excel workbook (`XLSX`).
- Current observed sizes:
  - MD: 2,098–5,372 bytes.
  - CSV: 149–791 bytes.
  - XLSX: 9,505–34,368 bytes.
- Largest observed attachment: CRM XLSX workbook at 34,368 bytes.
- These sizes are far below Gumroad's documented paid-product per-file ceiling of 20 GB.

Gumroad's Help Center says an individual file on a paid product can be up to 20 GB; free products have a lower limit. Do not infer that every file type is readable in the Gumroad mobile app. The documented mobile-friendly list includes PDF/EPUB, common audio, and common video formats; MD/CSV/XLSX are not on that list.

References:
- File size limits: https://gumroad.com/help/article/ (Help Center → Add a product → File size limits)
- Mobile-friendly file types: https://gumroad.com/help/article/112-mobile-friendly-files
- Ebook size/readability details: https://gumroad.com/help/article/357-sell-an-ebook

### 2.2 Delivery rules

- Keep the current three-file product structure unless a product-specific reason justifies a change.
- File extensions and actual MIME/content must agree. Do not rename a file to an extension it does not actually use.
- Test every XLSX in a real spreadsheet parser; verify formulas, validations, sheet names, and workbook opening.
- Test CSV encoding as UTF-8, delimiter consistency, header names, and row shape.
- Markdown must render cleanly and contain no broken relative links.
- Keep filenames short, descriptive, and ASCII-safe. Use lowercase kebab-case for new filenames.
- Do not upload source assets, temporary build files, credentials, debug logs, or unrelated files as buyer deliverables.
- Add PDF/EPUB only when the product benefits from a reader-friendly/mobile-friendly companion. Do not create redundant formats merely to inflate the file count.
- Preserve buyer-facing file order: quick-start guide first, worksheet second, workbook third.

## 3. Gumroad cover images and thumbnails

### 3.1 Cover image limits

Gumroad's current cover guidance:
- Supported uploaded cover types: PNG, JPEG, MOV, GIF. YouTube/Vimeo links can also be embedded.
- Maximum: 8 cover items per product.
- Recommended minimum image dimensions: 1280 × 720 px.
- Resolution: at least 72 DPI.
- Each uploaded image cover must be **under 50 MB**.
- Images whose longest side exceeds 4096 px are automatically resized; GIFs are not resized.
- Gumroad recommends using a still image as the first cover and keeping multiple covers at the same aspect ratio for a stable gallery.
- A PDF is not a valid cover image.
- Avoid these characters in cover filenames: `# $ _ + & ; : %`. Use simple names such as `business-launch-cover-01.png`.

Official reference: https://gumroad.com/help/article/60-adding-a-cover-image

### 3.2 Thumbnail is a separate asset

- A product thumbnail is not the first cover and is not interchangeable with the cover gallery.
- Minimum thumbnail size: 600 × 600 px.
- Thumbnails are used in the buyer library, Gumroad Discover, and profile surfaces.
- The current Gumroad product API audit returned five image covers per product. It does not prove that a separate thumbnail has been assigned.
- Do not call `add_cover` to set a thumbnail: that endpoint adds a gallery cover. Use the Gumroad product editor/official supported thumbnail workflow and verify the result independently.

### 3.3 Current repository export dimensions

The existing `.github/workflows/render-product-covers.yml` uses `librsvg2-bin` on Ubuntu 22.04 and renders SVG sources to PNG as follows:

| Asset path/pattern | Current generated dimensions | Purpose |
|---|---:|---|
| `products/**` SVG (except `thumbnail.svg`) | 1600 × 1000 px | Product cover/gallery and preview artwork |
| `storefront/brand-avatar.svg` | 1024 × 1024 px | Brand avatar |
| `storefront/favicon.svg` | 128 × 128 px | Favicon |
| `storefront/brand-wordmark.svg` | 1600 × 400 px | Horizontal wordmark |
| `marketing/**/*.svg` | 1000 × 1500 px | Vertical campaign artwork |

The current product export (1600 × 1000) exceeds Gumroad's minimum width and height. It is a 16:10 canvas, not 16:9; this is valid under Gumroad's guidance. Keep all images in one product gallery at a consistent ratio. Do not change source art or export dimensions globally without checking every asset class.

**Automated compliance gate added:** `scripts/validate_gumroad_assets.py` now inspects generated PNG headers and checks product image dimensions, 72 DPI metadata, the 4096 px longest-side threshold, the under-50-MiB cover limit, the 600 × 600 square thumbnail rule, and fixed brand/campaign dimensions. `tests/test_validate_gumroad_assets.py` covers valid covers, undersized covers, DPI, thumbnails, and the size ceiling. The render workflow now requests 96 DPI and runs the unit tests plus the validator before committing rendered assets. The first CI run after this change still needs a confirmed successful result; until then, treat the new gate as implemented but not yet proven in CI. The workflow continues to exclude `thumbnail.svg` from rendering, so thumbnail source export/assignment remains a separate task.

## 4. Current GitHub Actions toolchain

### 4.1 Workbook build and regression workflow

File: `.github/workflows/build-product-workbooks.yml`

- Runner: Ubuntu 22.04.
- Python: 3.12.
- Dependency: `openpyxl`.
- Regression test: `python -m unittest discover -s tests -p "test_build_product_workbooks.py" -v`.
- Build script: `scripts/build_product_workbooks.py`.
- Generates ten XLSX workbooks and verifies the expected output count before committing them.
- Existing tests cover workbook count/openability, the 30-day calendar, 100-hook rows, CRM formulas/dropdowns, and pricing formulas.

### 4.2 Image rendering workflow

File: `.github/workflows/render-product-covers.yml`

- Runner: Ubuntu 22.04.
- Renderer: `librsvg2-bin` / `rsvg-convert`.
- Renders SVG sources to PNG at the fixed dimensions in §3.3 and requests 96 DPI metadata.
- Expects 53 SVG source files to be rendered.
- Runs `tests/test_validate_gumroad_assets.py` and `scripts/validate_gumroad_assets.py` before committing.
- Commits rendered PNGs back to `main` only after the compliance gate passes.
- Raster optimization and dedicated thumbnail rendering/assignment remain separate follow-up work.

### 4.3 GitHub Actions guardrails

- Workflow YAML files must remain below 500 KB.
- Avoid uploading buyer deliverables or large image collections as workflow artifacts unless needed; repository Actions storage quotas depend on plan.
- Pin third-party Actions to reviewed versions or immutable commit SHAs for security-sensitive production workflows.
- Keep permissions least-privilege. The current asset/workbook workflows need repository content write access only because they commit generated files.
- Never put Gumroad tokens, deploy tokens, API keys, or customer data in source files or workflow logs. Use repository/environment secrets only when a verified workflow actually needs them.

Official reference: https://docs.github.com/en/actions/reference/limits

## 5. Free/open-source production tools

Prefer reproducible CLI tools in GitHub Actions over manual one-off editing.

| Tool | License / role | Use in this repository |
|---|---|---|
| Python 3 | Open source | Build scripts, validators, tests |
| openpyxl | MIT | XLSX generation and regression checks |
| librsvg / rsvg-convert | LGPL | Current SVG → PNG rendering tool |
| Pillow | HPND | Read dimensions, inspect image modes, convert/optimize raster images |
| ImageMagick | Apache 2.0 | Batch image inspection, conversion, resizing |
| Inkscape | GPL | Vector artwork editing/export |
| GIMP | GPL | Raster artwork and manual image correction |
| SVGO | MIT | Optimize SVG source without changing intended appearance |
| oxipng | MIT | Lossless PNG optimization |
| pngquant | GPL-3.0 | Optional lossy PNG palette reduction; visually inspect results |
| gifsicle | GPL | GIF optimization; preserve animation and verify frame timing |
| FFmpeg | LGPL/GPL depending on build | Video/GIF conversion and compression |
| Playwright | Apache 2.0 | Browser-based page checks and screenshots |
| Lighthouse | Apache 2.0 | Performance, accessibility, SEO and best-practice audits |
| axe-core | MPL-2.0 | Automated accessibility checks |
| html-validate | MIT | HTML structure and accessibility-oriented linting |

Project sources:
- https://github.com/python-pillow/Pillow
- https://github.com/ImageMagick/ImageMagick
- https://gitlab.gnome.org/GNOME/librsvg
- https://github.com/inkscape/inkscape
- https://github.com/GNOME/gimp
- https://github.com/svg/svgo
- https://github.com/oxipng/oxipng
- https://github.com/kornelski/pngquant
- https://github.com/kohler/gifsicle
- https://github.com/FFmpeg/FFmpeg
- https://github.com/microsoft/playwright
- https://github.com/GoogleChrome/lighthouse
- https://github.com/dequelabs/axe-core
- https://github.com/html-validate/html-validate

Use only original assets or assets whose licenses explicitly permit the intended commercial use. Record attribution and license evidence for third-party assets.

## 6. Release checklist — must pass before publishing

### Product and delivery
- [ ] Product title, description, price, file list, and actual files match.
- [ ] All 3 expected files are present and open correctly.
- [ ] XLSX formulas and dropdowns are tested; CSV and Markdown pass validation.
- [ ] Download links are not exposed publicly outside the buyer-delivery flow.
- [ ] Product URL resolves to the correct Gumroad listing.

### Covers and thumbnails
- [ ] First cover is a static PNG/JPEG image, not a video/GIF.
- [ ] Every uploaded cover is PNG/JPEG/GIF/MOV or a supported video embed.
- [ ] Every image cover is at least 1280 × 720 px and at least 72 DPI.
- [ ] Every image cover is under 50 MB and no dimension exceeds 4096 px unless GIF.
- [ ] All gallery images for one product use the same aspect ratio.
- [ ] Product thumbnail is separately verified at 600 × 600 px minimum.
- [ ] Filenames avoid Gumroad's documented special-character list.
- [ ] Image is legible on desktop and mobile; inspect actual crop and text at display size.

### Storefront and deployment
- [ ] Preview custom Gumroad page with `gumroad pages preview`.
- [ ] Confirm the page does not accidentally remove important profile sections/content.
- [ ] Publish through `gumroad pages push profile` only after preview approval.
- [ ] Confirm all purchase links point to canonical Gumroad product URLs.
- [ ] Do not link to raw downloadable files from the custom page.
- [ ] If an external marketing site is used, confirm host terms permit commercial use and verify HTTPS, mobile layout, SEO metadata, links, and image loading.

### Engineering and security
- [ ] Run the repository's documented tests and workflows.
- [ ] Run image size/dimension/DPI validation; do not rely on render success alone.
- [ ] Check HTML, accessibility, broken links, browser console, and mobile layout.
- [ ] No secrets, credentials, private buyer files, or unlicensed assets are committed.
- [ ] Record provider, tool versions, workflow run, and any manual exceptions.

## 7. Known gaps and non-assumptions

- Gumroad's product connector does not expose the native custom-profile publishing operation; the official CLI/UI route is documented above.
- Five gallery covers per product were verified. A separate thumbnail assignment has not been verified.
- Current image workflow renders 53 SVGs to PNG but does not enforce file byte limits or DPI metadata.
- Current Gumroad attachments are MD/CSV/XLSX and small; that does not establish mobile-app readability for those formats.
- No external host is configured or deployed by this document.
- Do not claim a site, profile page, thumbnail, or asset is published/assigned until the relevant provider confirms it and a public URL or product record is checked.
