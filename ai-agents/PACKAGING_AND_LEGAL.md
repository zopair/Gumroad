# Packaging, Security & Legal Release Standard

## Per-product ZIP layout

```text
<product-slug>/
├── LICENSE                         # exact upstream license, preserved
├── NOTICE                          # if upstream/dependencies require it
├── ATTRIBUTION.md                  # upstream source, commit, modifications
├── THIRD-PARTY-LICENSES.md         # generated and manually reviewed inventory
├── README.md
├── START-HERE.md
├── CHANGELOG.md
├── SECURITY.md
├── PRIVACY.md
├── .env.example                    # placeholders only
├── app/
│   ├── frontend/
│   ├── backend/
│   ├── agents/
│   ├── tools/
│   ├── prompts/
│   └── config/
├── branding/
│   ├── brand.json
│   ├── logo.svg
│   ├── favicon.svg
│   └── theme.css
├── deployment/
│   ├── local/
│   └── serverless/
├── examples/
│   ├── sample-input/
│   └── sample-output/
├── scripts/
│   ├── install.sh
│   ├── install.ps1
│   └── health-check.py
└── tests/
    ├── unit/
    ├── integration/
    └── security/
```

Only include folders and scripts that exist and are tested for that product. Do not ship empty placeholder directories or claim cross-platform support without testing.

## Architecture and cost discipline

- Prefer stateless request handlers for serverless deployment.
- Use local SQLite or filesystem storage for single-user/local editions; do not require managed databases unless a real multi-user feature requires them.
- Make external model/data providers adapters, not hard-coded dependencies.
- Allow user-supplied API keys through environment variables or an OS-backed secret store.
- Add timeouts, retries with bounded backoff, rate limits, and request-size limits.
- Cache repeatable public research where legally permitted; expose cache age and refresh controls.
- Offer deterministic/local functionality when it does not compromise product value.
- Do not make an always-on worker the default for workloads that can run on demand.
- Disclose estimated provider costs and the fact that third-party API usage is paid separately where applicable.

## Legal compliance

- Preserve upstream LICENSE verbatim.
- Preserve applicable NOTICE and copyright headers.
- Include a clear modification notice and exact upstream commit.
- Inventory direct and transitive dependency licenses; review models, datasets, fonts, icons, sample files, and assets separately.
- Reject non-commercial or otherwise incompatible dependencies from the commercial package unless replaced with eligible alternatives.
- Do not claim that the entire product is MIT/Apache merely because its primary upstream is.
- Include user-facing terms/limitations for financial, legal, privacy, email, scraping, and platform integrations.
- Do not redistribute API credentials, paid datasets, proprietary model weights, or external content without permission.

## Security baseline

- Secret scanning and dependency vulnerability scan.
- No secrets in source, ZIP, screenshots, logs, tests, or sample env values.
- Validate uploads by MIME, extension, size, and parser safety; store outside executable paths.
- Sandbox document parsing and any code analysis that could invoke tools.
- Restrict outbound network destinations where possible.
- Avoid shell execution and browser automation by default.
- Add deletion and retention behavior for uploaded files and user data.
- Log metadata without logging document contents, secrets, or full personal data.
- Human approval before publishing, sending, trading, or applying code changes.

## Required release tests

1. Fresh install on a clean supported environment.
2. Configuration validation and missing-key error handling.
3. Main happy path with deterministic fixture data.
4. Invalid input, oversized file, malformed document, and provider timeout.
5. Data deletion and no-secret leakage checks.
6. License/NOTICE presence and dependency audit.
7. ZIP integrity and exact file manifest.
8. Screenshots captured from the actual tested build.
9. User guide matches the actual product.
10. Gumroad ZIP download and extracted folder tested.

## Release decision

A product is releasable only when every mandatory test passes and its legal audit is marked approved. A source candidate or marketing page alone is not a release.
