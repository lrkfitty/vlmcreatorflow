# Autonomous GTM Stack — CreateFlow

**Purpose:** Use OpenClaw as the autonomous operator across the entire go-to-market motion.
You set the strategy. The agents do the work.

---

## The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                     YOU (The Conductor)                         │
│         Set strategy, review outputs, approve high-stakes sends │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │    OPENCLAW       │  ← The autonomous operator
                    │  (your AI brain)  │     Reads directives,
                    │                   │     routes to agents,
                    └────────┬──────────┘     runs scripts
                             │
        ┌────────────────────┼─────────────────────┐
        │                    │                     │
   ┌────▼────┐         ┌─────▼──────┐       ┌─────▼──────┐
   │PERPLEXITY│         │   CLAUDE   │       │  CREATEFLOW │
   │Research  │         │ Copy/Ops   │       │  Production │
   └──────────┘         └────────────┘       └─────────────┘
```

---

## Phase 1: Prospecting (Find the Right Companies)

**Goal:** Build a targeted list of companies that match each enterprise niche.

**Agent:** OpenClaw + Perplexity skill + `execution/scrape_leads.py`

### What OpenClaw does autonomously:
1. Reads `directives/lead_generation.md` for niche criteria
2. Calls Perplexity: *"Find 50 mid-sized ad agencies in the US with 10–100 employees, LinkedIn presence, and active digital marketing spend"*
3. Runs `execution/scrape_leads.py` to enrich the list (company name, founder name, email pattern, pain points)
4. Saves structured output to `.tmp/leads_<niche>_<date>.csv`
5. Pushes the CSV to Google Sheets (your live CRM)

### Output format (Google Sheet):
| Company | Founder | Email | LinkedIn | Niche | Pain Point | Score |
|---------|---------|-------|----------|-------|------------|-------|
| AdCo | Jane S | jane@adco.com | /in/janes | Agency | High shoot cost | 87 |

### Trigger (send this via Telegram):
```
prospect: ad agencies, 50 leads, US market
```

---

## Phase 2: Outreach (Contact Them Without You Lifting a Finger)

**Goal:** Send personalized cold emails using the Escape-to-Arrival framework.

**Agent:** OpenClaw + Claude + `execution/send_email.py`

### What OpenClaw does autonomously:
1. Reads the qualified lead list from Google Sheets
2. Tells Claude: *"Draft a personalized cold email for [Company], founder [Name], in the [Niche] space using the Escape-to-Arrival framework. Their pain: [Pain Point]. Keep it under 120 words. Subject line + body."*
3. Claude writes the email — different every time, personalized per lead
4. OpenClaw runs `execution/send_email.py` (via SendGrid) with a 3-day follow-up queued automatically
5. Logs sent emails back to Google Sheets with timestamp + status

### Email sequence (automated):
- **Day 0:** Cold intro (Escape frame — their pain)
- **Day 3:** Follow-up (Arrival frame — the result)
- **Day 7:** Final nudge + free demo offer
- **Day 14:** Breakup email (creates urgency)

### Trigger:
```
outreach: send sequence to ad_agencies sheet, niche=ad agencies
```

---

## Phase 3: Communication (Manage Replies Without You Reading Every Email)

**Goal:** Monitor inbound replies and respond intelligently.

**Agent:** OpenClaw + Claude + `execution/monitor_inbox.py`

### What OpenClaw does autonomously:
1. `execution/monitor_inbox.py` polls your outreach inbox every 60 minutes
2. For each reply, Claude classifies it:
   - **Interested** → drafts a warm reply + books a demo link
   - **Not now** → drafts a graceful re-engagement for 30 days later
   - **Objection** → drafts a rebuttal (price, trust, timing)
   - **Unsubscribe** → removes from list, logs
3. Draft reply is saved to `.tmp/reply_drafts/`
4. OpenClaw pings you on Telegram: *"Reply from Jane @ AdCo — classified: Interested. Draft ready for review."*
5. You send one message back: `approve` or `edit: [your change]` → it sends

### The key: You never write a cold reply from scratch again.
You only review and approve. Takes you 30 seconds per lead.

---

## Phase 4: Marketing & Advertising (Content That Sells Itself)

**Goal:** Generate and distribute content that attracts inbound leads automatically.

**Agent:** OpenClaw + Perplexity + Claude + CreateFlow

### Weekly content loop (runs automatically every Monday):

1. **Research** (Perplexity): *"What are the top 3 trending pain points for ad agencies this week?"*
2. **Strategy** (Claude): Write a LinkedIn post, email newsletter snippet, and ad headline for each pain point
3. **Visuals** (CreateFlow): Generate 3 on-brand images — one per piece of content — using the CreateFlow API
4. **Package**: Zip content + images into `.tmp/weekly_content_<date>/`
5. **Distribute**: Push to Buffer/Later for scheduled social posting + add to email drip

### Trigger (set it and forget it):
```
schedule: weekly_content_loop every Monday at 9am
```

### Paid Ad Creation:
When you want to run ads, send:
```
create ad creative: niche=real estate, angle=lifestyle shots, platform=Meta
```
OpenClaw runs CreateFlow to generate the images + Claude writes the ad copy + outputs a complete Meta ad package (image + headline + body + CTA) to `.tmp/ads/`.

---

## Phase 5: Conversion (Turn Self-Serve Visitors Into Paying Users)

**Goal:** Automate the conversion journey for the $49/mo self-serve tier without you being in the loop.

**Agent:** OpenClaw + Claude + Stripe webhooks + `execution/conversion_ops.py`

### The automated self-serve funnel:

```
Visitor lands on landing page
        ↓
Signs up for free trial (Stripe Checkout)
        ↓
Stripe webhook fires → OpenClaw receives event
        ↓
Claude writes personalized onboarding email (based on niche they selected)
        ↓
Day 3: OpenClaw checks if they've generated any images (via CreateFlow usage API)
  → If NO: sends "stuck?" nudge email + tutorial link
  → If YES: sends "you're crushing it" engagement email + upsell to annual plan
        ↓
Day 7: Non-converters get a "your trial ends soon" urgency sequence
Day 14: Trial ends → Stripe charges → success email sent automatically
```

### Churn intervention (automated):
```
execution/monitor_churn.py runs daily:
- Flags any paying user with 0 generations in 7 days
- OpenClaw tells Claude to write a re-engagement email
- You get a Telegram ping: "3 users at churn risk — re-engagement drafted"
```

---

## The Full Autonomous Loop (Daily Operations)

```
Morning (automated, no input from you):
  → Check inbox for replies → classify → draft responses → ping you
  → Check churn signals → draft re-engagement → ping you
  → Post scheduled social content (from Monday batch)

Weekly (one Telegram message from you):
  → "prospect: [niche], [count] leads"
  → "outreach: send to [sheet name]"
  → "weekly_content_loop" (if not scheduled)

Monthly (you review the dashboard):
  → Google Sheets: leads added, emails sent, replies received, conversions
  → You adjust strategy → update directives/ → agents adapt
```

---

## Scripts Needed (for Claude Code to build)

| Script | Purpose |
|--------|---------|
| `execution/scrape_leads.py` | Perplexity-powered lead enrichment → CSV |
| `execution/send_email.py` | SendGrid email sending + queue management |
| `execution/monitor_inbox.py` | Poll inbox, classify replies, draft responses |
| `execution/conversion_ops.py` | Stripe webhook handler + onboarding sequences |
| `execution/monitor_churn.py` | Daily usage check + churn intervention |
| `execution/weekly_content.py` | Research + write + generate visuals for content |
| `execution/push_to_sheets.py` | Write any dataset to Google Sheets (shared CRM) |

---

## What You Actually Do Every Day

| Your Role | Time Required |
|-----------|--------------|
| Approve/edit reply drafts (Telegram) | 5–10 min |
| Review weekly content before publish | 10 min |
| Monthly strategy + directive updates | 1–2 hours |
| Client onboarding (new enterprise client) | 2–3 hours (once) |

**Everything else runs itself.**

---

## API Keys Needed (add to `.env`)

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxx         # Claude
PERPLEXITY_API_KEY=pplx-xxxxxxx          # Research
SENDGRID_API_KEY=SG.xxxxxxx              # Email sending
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxx      # Conversion tracking
GOOGLE_SHEETS_ID=xxxxxxx                 # Your CRM sheet
```
