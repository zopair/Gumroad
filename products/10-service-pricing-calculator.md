# Service Pricing Calculator Workbook

Use your own cost, tax and fee assumptions. This worksheet is not tax or financial advice.

## Inputs
| Variable | Value | Notes |
|---|---:|---|
| Desired monthly owner compensation | | Before personal tax |
| Monthly fixed business costs | | Software, rent, insurance |
| Monthly variable costs | | Delivery-related |
| Available work hours / month | | Exclude leave and admin |
| Billable utilization | | Enter as decimal, e.g. 0.60 |
| Target operating margin | | Enter as decimal |
| Payment/platform fee rate | | Use actual provider schedule |
| Contingency reserve rate | | Optional |

## Core calculations
- Billable hours = available work hours × utilization
- Required revenue before variable payment fees = (owner compensation + fixed costs + variable costs) ÷ (1 − target margin)
- Effective hourly floor = required revenue ÷ billable hours
- Quote price = estimated delivery hours × effective hourly floor + project-specific costs

If fees are charged as a percentage of revenue, include them in the denominator: 1 − target margin − fee rate. If this denominator is zero or negative, the assumptions are not viable.

## Quote worksheet
| Task | Estimated hours | Risk factor | Adjusted hours |
|---|---:|---:|---:|
| Discovery | | | |
| Preparation | | | |
| Delivery | | | |
| Review / revisions | | | |
| Handoff | | | |
| Total | | | |

Adjusted hours = estimated hours × (1 + risk factor).

## Scenario comparison
| Scenario | Utilization | Margin | Fee rate | Effective hourly floor |
|---|---:|---:|---:|---:|
| Conservative | 0.45 | 0.15 | 0.05 | |
| Base | 0.60 | 0.20 | 0.05 | |
| High utilization | 0.75 | 0.20 | 0.05 | |

Replace example assumptions with your own data.

## Decision checks
- Does the quote cover delivery, admin, revisions and handoff?
- Is scope specific enough to estimate?
- Is the client paying for outcomes or hours?
- What happens when scope changes?
- Is the price consistent with market evidence and your positioning?

## License
Personal and internal business use only. No resale or redistribution.