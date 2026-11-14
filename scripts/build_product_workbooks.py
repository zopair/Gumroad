from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter

NAVY = "243B53"
INK = "111827"
GOLD = "D6A85F"
IVORY = "F3F0E9"
WHITE = "FFFFFF"
PALE = "E8E3D8"
MUTED = "64748B"
GREEN = "E2F0E8"
RED = "FCE8E6"

PRODUCTS = {
    "01-business-launch-planner": "business-launch-planner.xlsx",
    "02-content-calendar": "30-day-content-calendar.xlsx",
    "03-content-hooks": "100-content-hooks.xlsx",
    "04-caption-workbench": "caption-writing-workbench.xlsx",
    "05-welcome-email-kit": "welcome-email-sequence.xlsx",
    "06-sales-follow-up-pack": "sales-follow-up-pack.xlsx",
    "07-simple-crm-lead-tracker": "simple-crm-lead-tracker.xlsx",
    "08-client-onboarding-pack": "client-onboarding-pack.xlsx",
    "09-proposal-sow-template": "proposal-sow-template.xlsx",
    "10-service-pricing-workbook": "service-pricing-calculator.xlsx",
}

THIN_GOLD = Side(style="thin", color=GOLD)
MEDIUM_NAVY = Side(style="medium", color=NAVY)


def read_text(root: Path, filename: str) -> str:
    path = root / filename
    return path.read_text(encoding="utf-8") if path.exists() else ""


def add_start_here(wb: Workbook, title: str, purpose: str, steps: list[str], notes: list[str] | None = None):
    ws = wb.active
    ws.title = "START HERE"
    ws.sheet_view.showGridLines = False
    ws["A1"] = title
    ws["A1"].font = Font(name="Aptos Display", size=22, bold=True, color=WHITE)
    ws["A1"].fill = PatternFill("solid", fgColor=INK)
    ws.merge_cells("A1:F1")
    ws["A3"] = "PURPOSE"
    ws["A3"].font = Font(bold=True, color=GOLD, size=11)
    ws["A4"] = purpose
    ws.merge_cells("A4:F5")
    ws["A4"].alignment = Alignment(wrap_text=True, vertical="top")
    ws["A7"] = "QUICK START"
    ws["A7"].font = Font(bold=True, color=GOLD, size=11)
    for i, step in enumerate(steps, start=8):
        ws.cell(i, 1, f"{i - 7}.")
        ws.cell(i, 2, step)
        ws.merge_cells(start_row=i, start_column=2, end_row=i, end_column=6)
        ws.cell(i, 2).alignment = Alignment(wrap_text=True, vertical="top")
    row = 9 + len(steps)
    if notes:
        ws.cell(row, 1, "IMPORTANT")
        ws.cell(row, 1).font = Font(bold=True, color=GOLD, size=11)
        for j, note in enumerate(notes, start=row + 1):
            ws.cell(j, 1, "•")
            ws.cell(j, 2, note)
            ws.merge_cells(start_row=j, start_column=2, end_row=j, end_column=6)
            ws.cell(j, 2).alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width = 20
    for col in "BCDEF":
        ws.column_dimensions[col].width = 22
    ws.row_dimensions[1].height = 42
    for r in range(4, 6):
        ws.row_dimensions[r].height = 28
    ws.freeze_panes = "A3"
    return ws


def style_table(ws, headers: list[str], widths: list[int] | None = None, freeze: str = "A2", filter_rows: bool = True):
    ws.sheet_view.showGridLines = False
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(1, col, header)
        cell.font = Font(bold=True, color=WHITE, size=10)
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = Border(bottom=MEDIUM_NAVY)
        if widths and col <= len(widths):
            ws.column_dimensions[get_column_letter(col)].width = widths[col - 1]
    ws.row_dimensions[1].height = 34
    ws.freeze_panes = freeze
    if filter_rows:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{max(ws.max_row, 2)}"
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if cell.row % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="F7F5F0")
    return ws


def dropdown(ws, cell_range: str, values: Iterable[str]):
    options = ",".join(values)
    dv = DataValidation(type="list", formula1=f'"{options}"', allow_blank=True)
    dv.error = "Choose a value from the list."
    dv.errorTitle = "Invalid choice"
    dv.prompt = "Select a value from the dropdown."
    ws.add_data_validation(dv)
    dv.add(cell_range)


def finish(wb: Workbook, path: Path):
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    wb.calculation.calcMode = "auto"
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def build_launch(root: Path, out: Path):
    wb = Workbook()
    add_start_here(wb, "BUSINESS LAUNCH PLANNER", "A decision workbook to test a business idea, define a narrow first offer and record evidence before committing more resources.", [
        "Complete Launch Brief with one reachable customer segment and one urgent problem.",
        "Use Evidence Log to record real conversations and observed workarounds.",
        "Define the first offer and list exclusions before estimating delivery.",
        "Enter your own costs and review the break-even calculation.",
        "Follow the 14-day sprint, then record a GO, REVISE or STOP decision."
    ], ["Compliments and hypothetical interest are weak demand signals; paid commitments and existing workarounds are stronger.", "This workbook is a planning aid, not legal, tax or financial advice."])
    ws = wb.create_sheet("Launch Brief")
    style_table(ws, ["Field", "Your input", "Notes"], [30, 42, 55])
    brief = [
        ("Working business name", "", "Use a temporary name if needed."),
        ("Customer segment", "", "Describe a specific, reachable group."),
        ("Urgent problem", "", "Use the customer's language."),
        ("Current alternatives", "", "What do they do today?"),
        ("Your solution", "", "Keep the first version narrow."),
        ("First offer", "", "Describe the paid outcome."),
        ("Delivery method", "", "How will the buyer receive it?"),
        ("Target launch date", "", ""),
        ("Main demand assumption", "", "What must be true for this to work?"),
        ("Biggest risk", "", "What could invalidate the idea?")
    ]
    for r in brief:
        ws.append(list(r))
    ws = wb.create_sheet("Evidence Log")
    style_table(ws, ["Date", "Customer segment", "Problem in their words", "Current workaround", "Evidence strength", "Source", "Follow-up", "Decision"], [14, 22, 38, 30, 20, 20, 28, 18])
    for _ in range(100):
        ws.append([""] * 8)
    dropdown(ws, "E2:E101", ["Weak", "Medium", "Strong"])
    ws = wb.create_sheet("Offer Design")
    style_table(ws, ["Offer element", "Your decision", "Review question"], [28, 42, 58])
    for row in [
        ("Core outcome", "", "What changes for the buyer?"),
        ("Included deliverables", "", "What exactly is delivered?"),
        ("Explicit exclusions", "", "What is not included?"),
        ("Delivery time", "", "When will the buyer receive it?"),
        ("Support boundary", "", "What support is and is not included?"),
        ("Price", "", "What is the buyer paying for?"),
        ("Revision / refund terms", "", "Are terms clearly stated?")
    ]:
        ws.append(list(row))
    ws = wb.create_sheet("Unit Economics")
    style_table(ws, ["Metric", "Amount", "How to use it"], [34, 20, 65])
    for row in [
        ("Selling price", 0, "Enter your actual selling price."),
        ("Platform and payment fees", 0, "Use the current fee schedule for your sales channel."),
        ("Variable cost per sale", 0, "Include costs that increase with each sale."),
        ("Contribution per sale", "=B2-B3-B4", "Calculated as price minus fees and variable costs."),
        ("Fixed launch costs", 0, "One-time costs you want to recover."),
        ("Break-even units", '=IF(B5>0,ROUNDUP(B6/B5,0),"")', "Estimated units required to recover fixed launch costs.")
    ]:
        ws.append(list(row))
    ws["B2"].number_format = ws["B3"].number_format = ws["B4"].number_format = ws["B5"].number_format = ws["B6"].number_format = '$#,##0.00'
    ws["B7"].number_format = "0"
    ws = wb.create_sheet("14-Day Sprint")
    style_table(ws, ["Day", "Action", "Evidence to collect", "Pass condition", "Status", "Notes"], [10, 34, 38, 38, 18, 30])
    sprint = [
        ("1–2", "Define one customer segment", "10 target profiles", "Segment is reachable"),
        ("3–5", "Conduct problem interviews", "5 detailed conversations", "Repeated pain, not praise"),
        ("6–7", "Review alternatives", "5 competing offers", "Clear gap or differentiation"),
        ("8–10", "Build the smallest useful version", "A working sample", "A user can complete one task"),
        ("11–12", "Offer a paid pilot", "Price objections and commitments", "At least one real commitment"),
        ("13–14", "Make a decision", "Evidence summary", "Continue, revise or stop")
    ]
    for row in sprint:
        ws.append([row[0], row[1], row[2], row[3], "Not started", ""])
    dropdown(ws, "E2:E7", ["Not started", "In progress", "Done", "Blocked"])
    ws = wb.create_sheet("Launch Checklist")
    style_table(ws, ["Check", "Status", "Evidence / notes"], [48, 18, 55])
    for item in ["Product works from a clean copy", "Instructions and limitations are included", "Price and terms are clear", "Product page matches exact deliverables", "Support contact is monitored", "Analytics baseline is recorded", "First 10 relevant prospects are identified"]:
        ws.append([item, "Not started", ""])
    dropdown(ws, "B2:B8", ["Not started", "In progress", "Done", "Blocked"])
    finish(wb, out / PRODUCTS["01-business-launch-planner"])


def build_calendar(root: Path, out: Path):
    wb = Workbook()
    add_start_here(wb, "30-DAY CONTENT CALENDAR", "A monthly planning system that connects content topics to audience needs, business goals and measurable actions.", [
        "Set one monthly objective and define the primary audience.",
        "Add five content pillars that reflect real audience questions.",
        "Plan one topic, format and CTA for each day.",
        "Update status and results after publishing.",
        "Use Weekly Scorecard to review qualified actions, leads and sales."
    ], ["This is a planning workbook, not a scheduler or automated publishing integration.", "Use fictional sample content only for testing; replace it with your own material."])
    ws = wb.create_sheet("Setup")
    style_table(ws, ["Setting", "Your choice", "Guidance"], [30, 34, 65])
    for row in [
        ("Business / creator", "", "Brand or account name."),
        ("Audience", "", "Who is the content for?"),
        ("Primary offer", "", "What product or service does content support?"),
        ("Main platform", "", "Your highest-priority channel."),
        ("Secondary platform", "", "Optional."),
        ("Monthly objective", "Awareness", "Choose one primary objective."),
        ("Primary audience action", "", "One action per content item.")
    ]:
        ws.append(list(row))
    dropdown(ws, "B7", ["Awareness", "Leads", "Sales", "Retention"])
    ws = wb.create_sheet("Content Calendar")
    headers = ["Day", "Publish date", "Platform", "Format", "Content pillar", "Topic / hook", "Key point", "CTA", "Status", "Publish URL", "Reach", "Saves", "Shares", "Visits", "Leads", "Sales", "Notes"]
    style_table(ws, headers, [8, 15, 18, 18, 22, 38, 34, 22, 18, 34, 12, 12, 12, 12, 12, 12, 30])
    for day in range(1, 31):
        ws.append([day, "", "", "", "", "", "", "", "Idea", "", 0, 0, 0, 0, 0, 0, ""])
    dropdown(ws, "C2:C31", ["Instagram", "LinkedIn", "Facebook", "TikTok", "YouTube", "X", "Newsletter", "Other"])
    dropdown(ws, "D2:D31", ["Short video", "Carousel", "Story", "Text post", "Email", "Case study", "Live", "Other"])
    dropdown(ws, "E2:E31", ["Teach", "Demonstrate", "Explain / compare", "Behind the scenes", "Offer / objection", "Community"])
    dropdown(ws, "I2:I31", ["Idea", "Drafting", "Ready", "Scheduled", "Published", "Repurpose", "On hold"])
    ws = wb.create_sheet("Weekly Scorecard")
    style_table(ws, ["Metric", "Week 1", "Week 2", "Week 3", "Week 4", "Month total", "Review note"], [28, 15, 15, 15, 15, 18, 45])
    metrics = ["Reach", "Saves", "Shares", "Profile / site visits", "Leads", "Sales", "Qualified conversations"]
    for metric in metrics:
        ws.append([metric, 0, 0, 0, 0, f"=SUM(B{ws.max_row+1}:E{ws.max_row+1})", ""])
    ws = wb.create_sheet("Content Pillars")
    style_table(ws, ["Pillar", "Audience question", "Proof / asset available", "Desired action", "Topics to test"], [24, 38, 38, 24, 40])
    for pillar in ["Teach", "Demonstrate", "Explain / compare", "Behind the scenes", "Offer / objection handling"]:
        ws.append([pillar, "", "", "", ""])
    finish(wb, out / PRODUCTS["02-content-calendar"])


def parse_numbered_hooks(text: str):
    category = "General"
    hooks = []
    for line in text.splitlines():
        heading = re.match(r"^##\s+(.+)$", line.strip())
        if heading:
            category = heading.group(1).strip()
        match = re.match(r"^\s*(\d+)\.\s+(.+)$", line)
        if match:
            hooks.append((int(match.group(1)), category, match.group(2).strip()))
    return hooks


def build_hooks(root: Path, out: Path):
    text = read_text(root, "products/03-100-content-hooks.md")
    hooks = parse_numbered_hooks(text)
    if len(hooks) != 100:
        raise ValueError(f"Expected 100 hooks, found {len(hooks)}")
    wb = Workbook()
    add_start_here(wb, "100 CONTENT HOOKS", "A searchable hook library and adaptation worksheet for social posts, short-form video, newsletters and offer content.", [
        "Filter Hook Library by category or search for a phrase.",
        "Choose a hook that fits a real audience question.",
        "Adapt the opening and add one useful point or example.",
        "Verify every factual claim and add a relevant CTA.",
        "Record the final version in Adaptation Planner."
    ], ["Hooks are prompts, not guaranteed viral formulas.", "Do not invent statistics, testimonials or customer outcomes."])
    ws = wb.create_sheet("Hook Library")
    style_table(ws, ["ID", "Category", "Original hook", "Audience", "Platform", "Adapted opening", "Useful point", "Evidence / example", "CTA", "Claim checked"], [8, 26, 65, 24, 18, 55, 38, 38, 24, 16])
    for hook_id, category, hook in hooks:
        ws.append([hook_id, category, hook, "", "", "", "", "", "", "No"])
    dropdown(ws, "J2:J101", ["No", "Yes", "Needs review"])
    dropdown(ws, "E2:E101", ["Instagram", "LinkedIn", "Facebook", "TikTok", "YouTube", "X", "Newsletter", "Other"])
    ws = wb.create_sheet("Adaptation Planner")
    style_table(ws, ["Date", "Hook ID", "Audience", "Platform", "Adapted opening", "Useful point", "Proof / example", "CTA", "Claim checked", "Status"], [14, 12, 24, 18, 52, 38, 38, 24, 16, 18])
    for _ in range(50):
        ws.append(["", "", "", "", "", "", "", "", "No", "Draft"])
    dropdown(ws, "D2:D51", ["Instagram", "LinkedIn", "Facebook", "TikTok", "YouTube", "X", "Newsletter", "Other"])
    dropdown(ws, "I2:I51", ["No", "Yes", "Needs review"])
    dropdown(ws, "J2:J51", ["Draft", "Review", "Ready", "Published"])
    finish(wb, out / PRODUCTS["03-content-hooks"])


def build_captions(root: Path, out: Path):
    text = read_text(root, "products/04-caption-writing-workbench.md")
    patterns = []
    current = None
    body = []
    for line in text.splitlines():
        m = re.match(r"^###\s+(\d+)\.\s+(.+)$", line.strip())
        if m:
            if current:
                patterns.append((current[0], current[1], " ".join(body).strip()))
            current = (int(m.group(1)), m.group(2).strip())
            body = []
        elif current and line.strip() and not line.startswith("## "):
            body.append(line.strip())
    if current:
        patterns.append((current[0], current[1], " ".join(body).strip()))
    wb = Workbook()
    add_start_here(wb, "CAPTION WRITING WORKBENCH", "A practical drafting system for clear captions across Instagram, LinkedIn, X, Facebook and newsletters.", [
        "Choose one audience and one message.",
        "Select one of the 12 caption patterns.",
        "Complete the five-part drafting worksheet.",
        "Add evidence you can substantiate and one relevant CTA.",
        "Run the final quality gate before publishing."
    ], ["Do not fabricate proof, customer stories or performance claims.", "Adapt length and format to each platform."])
    ws = wb.create_sheet("12 Caption Patterns")
    style_table(ws, ["ID", "Pattern", "Framework / prompt", "Best use", "Notes"], [8, 26, 80, 28, 35])
    for pid, name, body_text in patterns:
        ws.append([pid, name, body_text, "", ""])
    ws = wb.create_sheet("Caption Drafts")
    style_table(ws, ["Date", "Platform", "Audience", "Problem / situation", "Opening", "Context", "Value / method", "Proof / source", "CTA", "Disclosure checked", "Final review", "Status"], [14, 18, 24, 34, 38, 34, 40, 36, 24, 18, 16, 18])
    for _ in range(50):
        ws.append(["", "", "", "", "", "", "", "", "", "No", "No", "Draft"])
    dropdown(ws, "B2:B51", ["Instagram", "LinkedIn", "Facebook", "X", "Newsletter", "Other"])
    dropdown(ws, "J2:J51", ["No", "Yes", "N/A"])
    dropdown(ws, "K2:K51", ["No", "Yes"])
    dropdown(ws, "L2:L51", ["Draft", "Review", "Ready", "Published"])
    ws = wb.create_sheet("5-Part Framework")
    style_table(ws, ["Step", "Purpose", "Your draft", "Quality check"], [18, 42, 60, 48])
    for row in [
        ("1. Opening", "Name a specific situation or problem.", "", "Does the first line identify a real audience?"),
        ("2. Context", "Explain why it matters.", "", "Is the context relevant and concise?"),
        ("3. Value", "Give one useful method or decision rule.", "", "Can the reader apply it?"),
        ("4. Proof", "Add a verifiable example or source.", "", "Can the claim be substantiated?"),
        ("5. Action", "Ask for one relevant next step.", "", "Is there one clear CTA?")
    ]:
        ws.append(list(row))
    finish(wb, out / PRODUCTS["04-caption-workbench"])


def build_email(root: Path, out: Path):
    wb = Workbook()
    add_start_here(wb, "WELCOME EMAIL SEQUENCE", "A five-email planning workbook for permission-based subscriber onboarding.", [
        "Confirm the exact signup promise and audience source.",
        "Draft each email in the Sequence Planner.",
        "Use the five-step sequence to deliver value before presenting an offer.",
        "Test every link, sender detail and unsubscribe mechanism.",
        "Send only to subscribers who appropriately opted in."
    ], ["Never use purchased or scraped addresses.", "This workbook does not send emails or connect to an email platform."])
    ws = wb.create_sheet("Sequence Planner")
    style_table(ws, ["Email", "Purpose", "Subject line", "Send delay (days)", "Key message", "CTA", "Signup promise delivered", "Consent checked", "Unsubscribe tested", "Links tested", "Status"], [10, 28, 38, 16, 50, 26, 22, 18, 18, 16, 18])
    sequence = [
        (1, "Deliver the promise", 0, "Send the resource or information requested."),
        (2, "Understand the problem", 2, "Explain a common obstacle and one useful first check."),
        (3, "Teach one method", 4, "Share a practical framework or mini-guide."),
        (4, "Address an objection", 7, "Answer a real question with honest fit / non-fit guidance."),
        (5, "Invite a next step", 10, "Present a relevant offer with clear deliverables and limitations.")
    ]
    for num, purpose, delay, message in sequence:
        ws.append([num, purpose, "", delay, message, "", "No", "No", "No", "No", "Draft"])
    dropdown(ws, "G2:J6", ["No", "Yes", "N/A"])
    dropdown(ws, "K2:K6", ["Draft", "Review", "Ready", "Scheduled", "Sent"])
    ws = wb.create_sheet("Email Drafts")
    style_table(ws, ["Email", "Subject option A", "Subject option B", "Opening", "Main content", "CTA / link", "Sender name"], [12, 34, 34, 42, 70, 28, 22])
    for i in range(1, 6):
        ws.append([i, "", "", "", "", "", ""])
    ws = wb.create_sheet("Compliance Checklist")
    style_table(ws, ["Check", "Status", "Evidence / notes"], [48, 18, 60])
    for item in ["Explicit opt-in recorded", "Signup promise matches sequence", "Sender identity and contact details present", "Unsubscribe mechanism works", "Suppression list respected", "Links and personalization tested", "Frequency matches signup promise", "No fabricated claims or fake scarcity"]:
        ws.append([item, "Not checked", ""])
    dropdown(ws, "B2:B9", ["Not checked", "Pass", "Fix required", "N/A"])
    finish(wb, out / PRODUCTS["05-welcome-email-kit"])


def build_followup(root: Path, out: Path):
    wb = Workbook()
    add_start_here(wb, "SALES FOLLOW-UP MESSAGE PACK", "A practical follow-up tracker and message planning workbook for permission-aware client communication.", [
        "Record the real context of the inquiry or proposal.",
        "Choose the relevant follow-up situation.",
        "Personalize the message using facts from the conversation.",
        "Set one next action and a due date.",
        "Record opt-outs and stop after a clear no."
    ], ["This is not an automated outreach or bulk messaging tool.", "Follow applicable privacy and marketing laws."])
    ws = wb.create_sheet("Follow-Up Tracker")
    style_table(ws, ["Contact / company", "Context", "Permission / lawful basis", "Last contact", "Message type", "Response status", "Next action", "Due date", "Owner", "Opt-out", "Notes"], [26, 34, 28, 16, 22, 20, 34, 16, 18, 14, 32])
    for _ in range(150):
        ws.append(["", "", "", "", "", "Not contacted", "", "", "", "No", ""])
    dropdown(ws, "F2:F151", ["Not contacted", "Sent", "Replied", "Waiting", "Closed", "No response"])
    dropdown(ws, "J2:J151", ["No", "Yes"])
    ws = wb.create_sheet("Message Library")
    style_table(ws, ["Situation", "Subject / opener", "Message goal", "Personalize with", "Stop / caution"], [30, 38, 36, 42, 48])
    messages = [
        ("New inbound inquiry", "Re: their request", "Confirm need and recommend a relevant next step.", "Specific need and one or two missing details.", "Do not assume a relationship."),
        ("After discovery", "Summary and next steps", "Confirm understanding, owners and dates.", "Goal, constraint, priority and open question.", "Invite corrections."),
        ("Proposal sent", "Checking the proposal", "Clarify scope, timeline or investment questions.", "The actual proposal and agreed follow-up timing.", "Avoid false urgency."),
        ("Decision support", "One point to help decide", "Explain a real trade-off between options.", "Verified differences and fit conditions.", "Do not pressure."),
        ("Close the loop", "Should I close this request?", "End the conversation respectfully.", "Last real contact and contact channel.", "Stop further follow-up unless invited."),
        ("Existing customer", "How is the deliverable working?", "Check delivery experience within agreed scope.", "Specific deliverable and support boundary.", "Do not imply unlimited support.")
    ]
    for row in messages:
        ws.append(list(row))
    finish(wb, out / PRODUCTS["06-sales-follow-up-pack"])


def build_crm(root: Path, out: Path):
    wb = Workbook()
    add_start_here(wb, "SIMPLE CRM & LEAD TRACKER", "A spreadsheet-ready lead pipeline for solo operators and small teams, with next-action discipline and a weekly dashboard.", [
        "Add one row per person or organization on Leads.",
        "Choose a pipeline stage and record the source and need.",
        "Assign an owner and next-action date to every open lead.",
        "Review Dashboard weekly and update stale records.",
        "Mark opt-outs and remove unnecessary personal data."
    ], ["Restrict access to people who need it.", "Do not store passwords, payment-card data or unnecessary sensitive information."])
    ws = wb.create_sheet("Leads")
    headers = ["Lead ID", "Created date", "Company", "Contact name", "Work email", "Source", "Need", "Estimated value", "Currency", "Stage", "Last contact", "Next action", "Next action date", "Owner", "Consent / basis", "Opt-out", "Notes"]
    style_table(ws, headers, [12, 15, 24, 22, 30, 18, 32, 18, 12, 18, 16, 32, 18, 18, 24, 14, 32])
    for i in range(1, 501):
        ws.append([f"L-{i:04d}", "", "", "", "", "", "", 0, "USD", "New", "", "", "", "", "", "No", ""])
    dropdown(ws, "F2:F501", ["Website", "Referral", "Social", "Email", "Event", "Other"])
    dropdown(ws, "I2:I501", ["USD", "EUR", "GBP", "EGP", "Other"])
    dropdown(ws, "J2:J501", ["New", "Contacted", "Qualified", "Proposal", "Won", "Lost", "Nurture"])
    dropdown(ws, "P2:P501", ["No", "Yes"])
    ws = wb.create_sheet("Dashboard")
    style_table(ws, ["Metric", "Value", "Definition"], [30, 18, 62])
    rows = [
        ("Total leads", "=COUNTA(Leads!A2:A501)", "Number of rows with a lead ID."),
        ("New", '=COUNTIF(Leads!J2:J501,"New")', "Leads not yet contacted."),
        ("Qualified", '=COUNTIF(Leads!J2:J501,"Qualified")', "Leads with need, fit and timing understood."),
        ("Proposals", '=COUNTIF(Leads!J2:J501,"Proposal")', "Proposals currently under consideration."),
        ("Won", '=COUNTIF(Leads!J2:J501,"Won")', "Opportunities marked won."),
        ("Lost", '=COUNTIF(Leads!J2:J501,"Lost")', "Opportunities marked lost."),
        ("Open pipeline value", '=SUMIF(Leads!J2:J501,"Qualified",Leads!H2:H501)+SUMIF(Leads!J2:J501,"Proposal",Leads!H2:H501)', "Sum of estimated values in Qualified and Proposal stages; use one currency per view."),
        ("Opt-outs", '=COUNTIF(Leads!P2:P501,"Yes")', "Records suppressed from further marketing.")
    ]
    for row in rows:
        ws.append(list(row))
    ws = wb.create_sheet("Pipeline Guide")
    style_table(ws, ["Stage", "Definition", "Exit condition", "Required next action"], [20, 42, 38, 38])
    for row in [
        ("New", "Lead received, not qualified.", "First relevant contact.", "Review inquiry."),
        ("Contacted", "Initial response sent.", "Reply or follow-up due.", "Set next contact date."),
        ("Qualified", "Need, fit and timing understood.", "Discovery complete.", "Define solution and scope."),
        ("Proposal", "Scope and price sent.", "Decision or revision.", "Clarify questions."),
        ("Won", "Agreement and payment process complete.", "Delivery handoff.", "Start onboarding."),
        ("Lost", "Not proceeding.", "Reason recorded.", "Close record."),
        ("Nurture", "Not ready; permission to follow up exists.", "Review date.", "Respect cadence and opt-outs.")
    ]:
        ws.append(list(row))
    finish(wb, out / PRODUCTS["07-simple-crm-lead-tracker"])


def build_onboarding(root: Path, out: Path):
    wb = Workbook()
    add_start_here(wb, "CLIENT ONBOARDING PACK", "A repeatable client-start process covering intake, kickoff, responsibilities, access security and handoff.", [
        "Send the welcome message and reference the approved scope.",
        "Collect only information required for the project.",
        "Run the kickoff and record decisions, owners and due dates.",
        "Grant named, least-privilege access with an expiry date.",
        "Complete handoff and remove unnecessary access."
    ], ["Adapt the workflow to your contract, industry and privacy obligations.", "This is not legal advice or secure file storage."])
    ws = wb.create_sheet("Onboarding Checklist")
    style_table(ws, ["Phase", "Task", "Owner", "Due date", "Status", "Dependency / reference", "Notes"], [20, 44, 20, 16, 18, 34, 32])
    tasks = [
        ("Before kickoff", "Confirm approved scope", "Provider"),
        ("Before kickoff", "Send welcome message", "Provider"),
        ("Intake", "Collect project goals and constraints", "Client"),
        ("Intake", "Confirm required deliverables", "Provider"),
        ("Kickoff", "Confirm stakeholders and decision owner", "Both"),
        ("Kickoff", "Agree timeline and feedback process", "Both"),
        ("Access", "Grant least-privilege named access", "Client"),
        ("Access", "Set MFA and access expiry", "Both"),
        ("Delivery", "Verify deliverables against acceptance criteria", "Provider"),
        ("Handoff", "Send organized files and instructions", "Provider"),
        ("Closeout", "Remove unnecessary access", "Provider")
    ]
    for phase, task, owner in tasks:
        ws.append([phase, task, owner, "", "Not started", "", ""])
    dropdown(ws, "E2:E12", ["Not started", "In progress", "Done", "Blocked"])
    ws = wb.create_sheet("Client Intake")
    style_table(ws, ["Question", "Client response", "Required?", "Notes"], [36, 52, 16, 36])
    for q in ["Organization", "Main contact and role", "Desired outcome", "Current situation", "Target audience", "Existing tools / systems", "Required deliverables", "Required integrations", "Constraints", "Approver", "Deadline and reason", "Accessibility / format needs", "Files supplied", "Information not to collect"]:
        ws.append([q, "", "Yes", ""])
    ws = wb.create_sheet("Kickoff Agenda")
    style_table(ws, ["Order", "Topic", "Decision / notes", "Owner", "Due date"], [10, 42, 52, 20, 16])
    for i, topic in enumerate(["Desired outcome and success criteria", "Scope, exclusions and assumptions", "Stakeholders and decision owner", "Timeline and dependencies", "Feedback and approval process", "Risks and escalation route", "Decisions and owners"], start=1):
        ws.append([i, topic, "", "", ""])
    ws = wb.create_sheet("Responsibility Matrix")
    style_table(ws, ["Work item", "Client", "Provider", "Approver", "Due date"], [32, 20, 20, 20, 16])
    for item in ["Supply source material", "Confirm requirements", "Review draft", "Final acceptance"]:
        ws.append([item, "", "", "", ""])
    ws = wb.create_sheet("Access & Security")
    style_table(ws, ["Control", "Status", "Evidence / owner"], [44, 18, 52])
    for item in ["Use least-privilege access", "Use named accounts; no shared passwords", "Enable MFA where available", "Transfer credentials through approved secret manager", "Define access expiry date", "Remove access at project close", "Avoid sensitive data in ordinary email"]:
        ws.append([item, "Not checked", ""])
    dropdown(ws, "B2:B8", ["Not checked", "Pass", "Fix required", "N/A"])
    finish(wb, out / PRODUCTS["08-client-onboarding-pack"])


def build_sow(root: Path, out: Path):
    wb = Workbook()
    add_start_here(wb, "PROPOSAL & STATEMENT OF WORK", "A reusable scope document to define outcomes, deliverables, acceptance criteria, milestones, fees, dependencies and change control.", [
        "Write the desired outcome in measurable, non-guaranteed terms.",
        "List each deliverable with acceptance criteria and due date.",
        "Record exclusions, assumptions and client dependencies.",
        "Complete fees and payment terms for the actual transaction.",
        "Use Change Log to document changes before work starts."
    ], ["This is a business template, not a legal contract or legal advice.", "Have transaction-specific terms reviewed by qualified counsel."])
    ws = wb.create_sheet("Proposal Summary")
    style_table(ws, ["Field", "Your details", "Guidance"], [30, 48, 60])
    for row in [
        ("Prepared for", "", "Client name and organization."),
        ("Prepared by", "", "Provider name."),
        ("Date / version", "", "Use version control."),
        ("Proposal validity", "", "State a real date or period."),
        ("Desired outcome", "", "Describe a business outcome without guaranteeing it."),
        ("Recommended approach", "", "Explain why the approach fits the constraints.")
    ]:
        ws.append(list(row))
    ws = wb.create_sheet("Deliverables")
    style_table(ws, ["ID", "Deliverable", "Acceptance criteria", "Format", "Owner", "Due date", "Status"], [10, 34, 48, 18, 18, 16, 18])
    for i in range(1, 16):
        ws.append([f"D{i}", "", "", "", "", "", "Draft"])
    dropdown(ws, "G2:G16", ["Draft", "In progress", "Review", "Accepted", "Blocked"])
    ws = wb.create_sheet("Milestones")
    style_table(ws, ["Milestone", "Provider action", "Client dependency", "Target date", "Status"], [24, 38, 38, 16, 18])
    for name in ["Discovery", "Draft", "Review", "Final handoff"]:
        ws.append([name, "", "", "", "Planned"])
    dropdown(ws, "E2:E5", ["Planned", "In progress", "Complete", "Blocked"])
    ws = wb.create_sheet("Fees & Assumptions")
    style_table(ws, ["Item", "Amount", "Currency", "Due date / condition", "Notes"], [28, 18, 14, 28, 42])
    for item in ["Discovery / setup", "Milestone 1", "Milestone 2", "Approved expenses", "Taxes / fees"]:
        ws.append([item, 0, "USD", "", ""])
    ws = wb.create_sheet("Change Log")
    style_table(ws, ["Request ID", "Requested change", "Reason", "Scope impact", "Cost impact", "Schedule impact", "Approved by", "Approval date", "Status"], [14, 34, 28, 30, 18, 18, 20, 18, 18])
    for _ in range(30):
        ws.append(["", "", "", "", "", "", "", "", "Draft"])
    dropdown(ws, "I2:I31", ["Draft", "Under review", "Approved", "Rejected", "Implemented"])
    ws = wb.create_sheet("Acceptance & Approval")
    style_table(ws, ["Field", "Agreed details"], [32, 90])
    for field in ["Review period", "Acceptance method", "Defect correction process", "Client name / role / date", "Provider name / role / date"]:
        ws.append([field, ""])
    finish(wb, out / PRODUCTS["09-proposal-sow-template"])


def build_pricing(root: Path, out: Path):
    wb = Workbook()
    add_start_here(wb, "SERVICE PRICING CALCULATOR", "A spreadsheet-based pricing model for service providers. Enter costs and capacity, compare utilization scenarios and estimate a project quote.", [
        "Enter your own compensation, costs, capacity and fee assumptions on Inputs.",
        "Review the effective hourly floor and verify the denominator is positive.",
        "Compare conservative, base and high-utilization scenarios.",
        "Estimate each project task and its risk factor on Quote Builder.",
        "Review the calculated quote against scope, market evidence and client fit."
    ], ["All values are examples until replaced with your own data.", "This is not tax, accounting or financial advice."])
    ws = wb.create_sheet("Inputs")
    style_table(ws, ["Variable", "Value", "Unit / guidance"], [38, 22, 72])
    inputs = [
        ("Desired monthly owner compensation", 3000, "Currency per month."),
        ("Monthly fixed business costs", 500, "Software, rent, insurance and other fixed costs."),
        ("Monthly variable costs", 200, "Monthly delivery-related variable costs."),
        ("Available work hours", 120, "Hours per month; exclude leave and admin."),
        ("Billable utilization", 0.60, "Decimal from 0 to 1."),
        ("Target operating margin", 0.20, "Decimal from 0 to 1."),
        ("Payment / platform fee rate", 0.05, "Use the actual provider fee schedule."),
        ("Contingency reserve rate", 0.00, "Optional reserve as a decimal.")
    ]
    for row in inputs:
        ws.append(list(row))
    ws["A11"] = "Required monthly revenue"
    ws["B11"] = '=IF(1-B7-B8>0,(B2+B3+B4)/(1-B7-B8),"CHECK ASSUMPTIONS")'
    ws["C11"] = "Includes target margin and percentage fee assumption."
    ws["A12"] = "Billable hours"
    ws["B12"] = "=B5*B6"
    ws["C12"] = "Available hours multiplied by utilization."
    ws["A13"] = "Effective hourly floor"
    ws["B13"] = '=IF(B12>0,B11/B12,"CHECK CAPACITY")'
    ws["C13"] = "Minimum hourly revenue implied by these assumptions."
    ws["B2"].number_format = ws["B3"].number_format = ws["B4"].number_format = ws["B11"].number_format = ws["B13"].number_format = '$#,##0.00'
    ws["B5"].number_format = '0.0'
    for cell in ["B6", "B7", "B8"]:
        ws[cell].number_format = "0.0%"
    dropdown(ws, "B6:B8", ["0.15", "0.20", "0.25", "0.30", "0.40", "0.45", "0.50", "0.60", "0.65", "0.70", "0.75", "0.80", "0.90"])
    ws = wb.create_sheet("Scenarios")
    style_table(ws, ["Scenario", "Utilization", "Target margin", "Fee rate", "Required monthly revenue", "Billable hours", "Hourly floor"], [22, 18, 18, 16, 28, 18, 20])
    for row in [
        ["Conservative", 0.45, 0.15, 0.05],
        ["Base", 0.60, 0.20, 0.05],
        ["High utilization", 0.75, 0.20, 0.05]
    ]:
        ws.append(row + [f'=IF(1-C{ws.max_row+1}-D{ws.max_row+1}>0,(Inputs!B2+Inputs!B3+Inputs!B4)/(1-C{ws.max_row+1}-D{ws.max_row+1}),"CHECK")', f"=Inputs!B5*B{ws.max_row+1}", f'=IF(F{ws.max_row+1}>0,E{ws.max_row+1}/F{ws.max_row+1},"CHECK")'])
    for r in range(2, 5):
        for c in ["B", "C", "D"]:
            ws[f"{c}{r}"].number_format = "0.0%"
        ws[f"E{r}"].number_format = ws[f"G{r}"].number_format = '$#,##0.00'
    ws = wb.create_sheet("Quote Builder")
    style_table(ws, ["Task", "Estimated hours", "Risk factor", "Adjusted hours", "Hourly floor", "Project costs", "Line quote"], [28, 18, 16, 18, 18, 18, 18])
    tasks = ["Discovery", "Preparation", "Delivery", "Review / revisions", "Handoff"]
    for i, task in enumerate(tasks, start=2):
        ws.append([task, 0, 0.10, f"=B{i}*(1+C{i})", "=Inputs!B13", 0, f"=D{i}*E{i}+F{i}"])
        ws[f"C{i}"].number_format = "0%"
        for col in ["E", "F", "G"]:
            ws[f"{col}{i}"].number_format = '$#,##0.00'
    ws.append(["TOTAL", "=SUM(B2:B6)", "", "=SUM(D2:D6)", "", "=SUM(F2:F6)", "=SUM(G2:G6)"])
    ws["G7"].font = Font(bold=True, color=GOLD)
    ws = wb.create_sheet("Quote Review")
    style_table(ws, ["Decision check", "Status", "Evidence / notes"], [46, 18, 60])
    for item in ["Quote covers delivery, admin, revisions and handoff", "Scope is specific enough to estimate", "Dependencies and client inputs are documented", "Risk factor is realistic", "Change process is clear", "Price is checked against market evidence", "Taxes and fees are verified"]:
        ws.append([item, "Not checked", ""])
    dropdown(ws, "B2:B8", ["Not checked", "Pass", "Fix required", "N/A"])
    finish(wb, out / PRODUCTS["10-service-pricing-workbook"])


def build_all(root: Path, out: Path):
    builders = [
        build_launch, build_calendar, build_hooks, build_captions, build_email,
        build_followup, build_crm, build_onboarding, build_sow, build_pricing
    ]
    for builder in builders:
        builder(root, out)
    files = sorted(out.glob("*.xlsx"))
    if len(files) != 10:
        raise RuntimeError(f"Expected 10 workbooks, generated {len(files)}")
    for file in files:
        check = load_workbook(file, read_only=True, data_only=False)
        if "START HERE" not in check.sheetnames:
            raise RuntimeError(f"{file.name} is missing START HERE")
        check.close()
    return files


if __name__ == "__main__":
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else root / "dist"
    built = build_all(root, out)
    for item in built:
        print(f"BUILT {item.name} {item.stat().st_size} bytes")
