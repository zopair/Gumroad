# JARVIS Brand & White-Labeling Standard

## Brand architecture

- Publisher: **Zubair Digital Kits**
- Product family: **JARVIS**
- Family descriptor: **Intelligent Business & Productivity Agents**
- Product naming: retain the approved product names (RankMaster AI, LeadScout Bot, TradeTrend Analyst, DocuSense Support, SocialSync AI, MailForge Pro, ContentFlip AI, EstateGuard AI, CodeSentinel, MarketMind AI).

## Visual system

| Token | Value | Usage |
|---|---|---|
| Charcoal | `#24272D` | Main dark background |
| Navy | `#142238` | Primary surfaces |
| Gold | `#D6B66D` | Accent, focus, key metrics |
| Ivory | `#F4F0E7` | Light surface and text |
| Muted | `#9AA4B2` | Secondary labels |

Use product-specific accent motifs and screenshots; do not reuse one generic cover across all ten products. Each cover must clearly state product name, primary outcome, and product family. Avoid fake interface screenshots: show only implemented UI or label concept visuals as concepts.

## Branding implementation

Keep brand values in one product-level configuration file (for example `branding/brand.json`) and reference those values in UI metadata, HTML title/description, theme tokens, favicon, and generated reports.

Do not perform blind global find-and-replace. First classify every upstream occurrence as:
1. UI display text — may be replaced where appropriate.
2. Package/module identifiers — change only with import/build/test updates.
3. Copyright/license/NOTICE/author attribution — preserve.
4. Security contact and provenance — update only if legally and operationally appropriate; retain upstream contacts where required.
5. API identifiers, database migrations, serialized formats — migration required; never rename casually.
6. Documentation history — retain upstream provenance and document modifications.

## Required product identity fields

- Product name and one-sentence purpose.
- Publisher attribution: Zubair Digital Kits.
- Product version and build date.
- Upstream project name, URL, commit SHA, and license.
- JARVIS modifications summary.
- Support and security contact configured by the publisher (do not invent one).
- Provider and model disclosures.

## Logo and asset rules

Use original JARVIS wordmark and product-specific iconography. Do not reuse upstream logos, avatars, screenshots, trademarks, or illustrations unless their license and trademark permissions explicitly allow it. Keep source LICENSE and NOTICE files in the package. Do not imply endorsement by upstream maintainers.
