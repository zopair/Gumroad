# Expense & Profit Tracker

## Transaction CSV schema
```csv
date,transaction_id,type,category,description,customer_or_vendor,project,amount,currency,tax_amount,payment_method,receipt_link,reconciled
```

Type must be Income or Expense. Keep source documents and follow local bookkeeping requirements.

## Suggested categories
**Income:** Product sales, services, subscriptions, refunds received, other income.  
**Expenses:** Software, contractors, advertising, payment fees, supplies, travel, rent, utilities, professional services, taxes, refunds, other.

## Monthly summary
| Metric | Formula |
|---|---|
| Gross income | Sum of income rows |
| Refunds / reversals | Sum of refund rows |
| Net income | Gross income − refunds |
| Operating expenses | Sum of operating expense rows |
| Operating result | Net income − operating expenses |
| Operating margin | Operating result ÷ net income |

Exclude taxes collected on behalf of authorities from revenue where applicable. Confirm classification with an accountant.

## Monthly close checklist
- [ ] Import all bank and payment-provider transactions
- [ ] Match each transaction to a receipt or invoice
- [ ] Identify duplicates
- [ ] Reconcile bank and platform balances
- [ ] Separate owner transfers from expenses
- [ ] Review refunds and chargebacks
- [ ] Review recurring subscriptions
- [ ] Lock the period after review

## Variance review
| Category | Budget | Actual | Difference | Explanation | Action |
|---|---:|---:|---:|---|---|
| | | | | | |

## License
Personal and internal business use only. No resale or redistribution.