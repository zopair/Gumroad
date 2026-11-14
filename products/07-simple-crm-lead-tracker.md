# Simple CRM & Lead Tracker

Create a spreadsheet with one row per person or organization. Restrict access to people who need it and store only necessary personal data.

## CSV header
```csv
lead_id,created_date,company,contact_name,work_email,source,need,estimated_value,currency,stage,last_contact,next_action,next_action_date,owner,consent_or_basis,opt_out,notes
```

## Pipeline stages
| Stage | Definition | Exit condition |
|---|---|---|
| New | Lead received, not qualified | First relevant contact |
| Contacted | Initial response sent | Reply or follow-up due |
| Qualified | Need, fit and timing understood | Discovery complete |
| Proposal | Scope and price sent | Decision / revision |
| Won | Agreement and payment process complete | Delivery handoff |
| Lost | Not proceeding | Reason recorded |
| Nurture | Not ready; permission to follow up exists | Review date |

## Required operating rules
1. Every active lead has one owner.
2. Every open lead has one next action and date.
3. Record source and context, not assumptions.
4. Never store passwords, payment-card data, or unnecessary sensitive details.
5. Mark opt-outs and suppress further marketing.
6. Review stale leads weekly.

## Weekly pipeline review
| Metric | Formula |
|---|---|
| New leads | Count created this week |
| Qualified rate | Qualified leads ÷ contacted leads |
| Proposal rate | Proposals ÷ qualified leads |
| Win rate | Won ÷ decided opportunities |
| Pipeline value | Sum estimated value of open qualified deals |
| Stale leads | Open leads with no next action date |

## Example rows (fictional)
```csv
L-001,2026-01-05,Northwind Demo,Sam Example,sam@example.invalid,Referral,Website refresh,1200,USD,Qualified,2026-01-06,Send scope questions,2026-01-08,Owner A,Existing inquiry,false,Illustrative data only
L-002,2026-01-06,Contoso Demo,Alex Sample,alex@example.invalid,Website,Content workflow,450,USD,New,2026-01-06,Review inquiry,2026-01-07,Owner A,Existing inquiry,false,Illustrative data only
```

## Setup checklist
- [ ] Freeze header row
- [ ] Add dropdowns for stage, owner, source and currency
- [ ] Validate dates and numeric fields
- [ ] Protect formula columns
- [ ] Set access permissions
- [ ] Define retention and deletion rules
- [ ] Test filters and weekly report

## License
Personal and internal business use only. No resale or redistribution.