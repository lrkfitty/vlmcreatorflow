# VLM CEO Agent Brief
> Complete operating knowledge for the VLM company CEO agent.
> Last updated: 2026-04-01

---

## What VLM Is

**Viral Lense Media (VLM)** — AI content studio and autonomous influencer platform.

Ty (Tylarkin) is the founder. He builds AI influencer accounts and sells AI content creation services to agencies, brands, and coaches. The goal is for everything except the sales call to run itself.

**Two products:**
1. **Creator Platform (B2C)** — self-serve AI image/video generation, consistent character creation. $49/mo (legacy) → $297/mo.
2. **Done-For-You AI Content (B2B)** — managed service. Custom AI influencer account, 2x daily autoposts, full pipeline. $1,500–3,000/mo. Never pitch $997 — that's a negotiation floor, not the anchor.

**Why VLM wins:** A single real photoshoot costs $20K+. VLM generates 100 AI creatives before lunch. The proof is live — Neo, Shay, and Ty are real accounts posting autonomously right now.

---

## Revenue Model

| Product | Current Price | Month 3 Target | Month 6 Target |
|---------|--------------|----------------|----------------|
| B2C self-serve | $49/mo | $297/mo | $297/mo |
| B2B managed | $997/mo | $1,500/mo | $3,000/mo |
| Enterprise (future) | — | — | $10,000/mo |
| Ad creative retainer (future) | — | — | $5,000/mo |
| AI Influencer deal (future) | — | — | $4,000/mo/character |

**Month 1 Goals (Apr 2026):**
- 50 cold agency outreaches
- 3 beta B2C users at $49/mo
- 2–3 managed B2B clients at $1,500/mo
- No enterprise or ad creative pitching yet — need case studies first

**Stripe:**
- B2B: `price_1TBzOvKIWXG1ZQJE9LYl49Ix` ($997/mo) — payment link: `https://buy.stripe.com/bJe28s3Ej9SX7XlgB78Vi08`
- B2C: `price_1TBzOvKIWXG1ZQJEyhifAvgr` ($49/mo) — payment link: `https://buy.stripe.com/28E3cweiX2qv7Xl0C98Vi09`

---

## The 3 AI Influencer Accounts (Live Proof)

| Account | Handle | Persona | Status |
|---------|--------|---------|--------|
| Neo | @neoismyname1 | Stoic/creative AI male, fashion + philosophy | Live, posting |
| Shay | @shay.so.fine | Luxury travel + fashion AI female | Live, posting |
| Ty | @tytheguyyttg | Tylarkin personal — Bangkok lifestyle | Live, posting |

**Content pipeline:**
1. Images generated via Flux Nano (Replicate API) — `execution/generate_image.py`
2. Videos via Kling AI v3.0 (JWT auth, polls until complete) — `execution/generate_video.py`
3. Human approval in dashboard or approved_posts.json
4. Auto-poster cron runs 10:00 AM + 10:00 PM Bangkok — `execution/auto_poster.py`
5. Logs to `.tmp/activity_log.json` and individual post logs

**Content is never auto-generated** — generation costs money. Only posting is automated. When the queue runs out, the cron logs a warning and stops.

**Output directories:**
- Neo: `output/users/Neo/Instagram/`
- Shay: `output/users/Shay/Instagram/`
- Ty (Tyrie): `output/users/Tyrie/Instagram/`

---

## The B2B Outreach Machine

Everything autonomous except the sales call itself.

### Pipeline Flow

```
Explorium API → leads.json → send_outreach.py → Gmail inbox → monitor_inbox.py → reply_drafts/ → sales call
```

### Lead Sourcing

- Tool: Explorium Vibe Prospecting API (`https://api.explorium.ai/v1/prospects`)
- API key: `6547e4ec-8cfa-4a94-a205-b47593591d50`
- **CRITICAL: 100 API credits are depleted.** Use `app.vibeprospecting.ai` chat interface (400 credits), export CSV, convert with `execution/source_leads.py --from-csv`
- 3 verticals: `ad_agency`, `financial_advisor`, `coach_consultant` — 10–20 leads each per run
- Stored in: `.tmp/leads.json`

### ICPs (Priority Order)

1. **Boutique Ad Agencies** — 10–50 employees, US-based. Founder/Creative Director/Head of Production. Pain: shoots cost $20K+, kills margins.
2. **Financial Advisors / Wealth Management** — RIAs, 1–20 employees, US. Pain: stock photography looks fake, real shoots $15K+.
3. **Coaching & Consulting** — solo to small teams, $500K–5M revenue. Pain: no time for shoots, want an AI avatar of themselves.

### Email Sequences (Escape-to-Arrival Framework)

4 emails per vertical, spaced Day 0 / 3 / 7 / 14:

| Email | Day | Theme |
|-------|-----|-------|
| 1 | 0 | **Escape** — vivid pain, broken current state |
| 2 | 3 | **Arrival** — transformation, live proof (Neo/Shay accounts) |
| 3 | 7 | **CTA** — book a call, $1,500–3,000/mo anchor, links to booking form |
| 4 | 14 | **Breakup** — "Closing your file" one-liner |

Templates: `execution/email_templates/` — 12 files (agency/financial/coaching × 4 emails)

**Sent from:** `hello@vlmcreateflow.com` (Namecheap Private Email, SMTP `mail.privateemail.com:587`)
**Reply-To:** `virallensemediavlm@gmail.com` (so Gmail MCP can monitor replies)

### Reply Monitoring

- Script: `execution/monitor_inbox.py`
- Monitors Gmail IMAP for replies from known lead emails
- App password: `hnyf uzpk ekjf lpto`
- Classification: keyword-only (no Anthropic API — per Ty's instruction, no paid tokens for classification)
- Unsubscribes → instant canned reply sent automatically
- All other replies → saved to `.tmp/reply_drafts/` with status `needs_draft`
- Review tool: `execution/send_draft.py`

### Booking Flow

- URL: `enterprise.vlmcreateflow.com` → B2B landing page with booking form at `?book=1`
- Built into Streamlit app — no Calendly (free Gmail doesn't support booking URLs)
- On submit: notifies Ty at both `tylarkin@vlmcreateflow.com` and personal email
- On submit: sends warm confirmation email to the lead from `hello@vlmcreateflow.com`

### Cron Jobs (Bangkok, 3 AM daily)

```
0  3 * * *   python3 execution/send_outreach.py    # drip sender
5  3 * * *   python3 execution/monitor_inbox.py    # inbox monitor
```

Instagram posts run at 10 AM and 10 PM Bangkok via system crontab (Python 3.11).

---

## Live Stack (as of Apr 2026)

### Websites (Vercel + Namecheap DNS)

| URL | Repo | Purpose |
|-----|------|---------|
| `vlmcreateflow.com` | lrkfitty/vlm-website | B2C creator marketing site |
| `enterprise.vlmcreateflow.com` | lrkfitty/vlm-enterprise | B2B enterprise sales + booking |
| `crm.vlmcreateflow.com` | flowleads.streamlit.app | CRM (Streamlit Cloud) |
| `b2b.vlmcreateflow.com` | vlmforbusiness.streamlit.app | B2B Streamlit funnel |

- Vercel auto-deploys on push to `main` (lrkfitty GitHub account)
- DNS: A record `@` → `76.76.21.21`, CNAME `enterprise` → Vercel
- Both sites: HTML/CSS/JS, video hero (Remotion-rendered MP4s), form → serverless function → SMTP + CRM
- Env var on Vercel: `SMTP_HELLO_PASS=Vlmcreateflow1!`

### Streamlit Apps (Streamlit Cloud, lrkfitty account)

| Repo | App URL | Custom URL |
|------|---------|------------|
| lrkfitty/vlm-b2b | vlmforbusiness.streamlit.app | b2b.vlmcreateflow.com |
| lrkfitty/vlm-b2c | createnow.streamlit.app | b2c.vlmcreateflow.com |
| lrkfitty/vlm-crm | vlmcreator.streamlit.app | crm.vlmcreateflow.com |
| lrkfitty/funnel | flowleads.streamlit.app | vlmcreateflow.com (redirect) |

Streamlit Cloud auto-deploys on push to `main`.

### Email Accounts

| Address | Password | Purpose |
|---------|----------|---------|
| hello@vlmcreateflow.com | Vlmcreateflow1! | Cold outreach sender, booking confirmations |
| noreply@vlmcreateflow.com | Vlmcreateflow1! | App notifications |
| tylarkin@vlmcreateflow.com | Larkin2017! | Receives lead + booking notifications |
| virallensemediavlm@gmail.com | App pw: `hnyf uzpk ekjf lpto` | Reply monitoring via IMAP |

---

## Command Center — How to Monitor Everything

### VLM Command Center (primary dashboard)

```
streamlit run vlm_command_center.py --server.port 8503
```

**Tabs:**
- `📸 Instagram` — account status (Neo/Shay/Ty), queue counts, cron schedule, recent activity log, last 5 posts
- `🎯 Funnel` — B2C + B2B pipeline stages, recent CRM leads table
- `📋 CRM Pipeline` — kanban view by stage (New → Contacted → Demo Booked → Won/Lost)
- `💰 Revenue` — MRR calculator (manual), revenue targets with progress bars
- `📧 Outreach` — lead sourcing stats, vertical breakdown, drip sequence progress, recent send log, full lead table, run buttons for sourcing + sending
- `⚡ Quick Actions` — post now (per account or all), deployment status, refresh

**Top metrics row (left to right):**
1. Posts Live (all 3 accounts combined)
2. Content Queued (Neo + Shay + Ty ready to post)
3. Outreach Leads (from leads.json)
4. Emails Sent (with reply + booked counts)
5. Calls Booked (with closed won)
6. MRR

### Visual Office (secondary, animated)

```
python3 office_server.py   # then open http://localhost:5001/visual_office
```

Canvas-based pixel art office. Agents at desks: Claude Code (orchestrator), Gemini (creative), Kling (video), Outreach Bot (sales), AutoPoster (ops), CRM Sync (ops), Gmail Monitor (reception).

---

## Agent Roster

| Agent | Tool | Responsibilities |
|-------|------|-----------------|
| Claude Code | Anthropic API (Sonnet) | Orchestrator — reads directives, routes tasks, runs scripts, self-anneals on errors |
| Gemini | Google AI | Creative direction, prompt writing, NL art direction |
| Kling AI | Kling v3.0 API | Video generation (JWT auth, polls for completion) |
| AutoPoster | `execution/auto_poster.py` | Posts approved content to Instagram 2x/day |
| Outreach Bot | `send_outreach.py` + `monitor_inbox.py` | Cold email drip + inbox monitoring |
| CRM Sync | Sheets integration | Syncs lead data to Google Sheets |

---

## What Runs Autonomously vs What Needs Ty

| Task | Autonomous? | Notes |
|------|-------------|-------|
| Instagram posting | ✅ Yes | Cron, 10AM + 10PM Bangkok |
| Cold email drip | ✅ Yes | Cron, 3AM Bangkok |
| Reply monitoring | ✅ Yes | Cron, 3:05AM Bangkok |
| Unsubscribe handling | ✅ Yes | Instant auto-reply |
| Booking confirmation email | ✅ Yes | Fires on form submit |
| Reply drafting | ❌ No | Drafts saved, Ty reviews + sends via `send_draft.py` |
| Content generation | ❌ No | Costs money — Ty triggers manually |
| Content approval | ❌ No | Ty approves before posting |
| Lead sourcing | ❌ No | API credits depleted — Ty sources via app.vibeprospecting.ai |
| Sales calls | ❌ No | Always Ty |
| Pricing decisions | ❌ No | Always Ty |

---

## File Locations (Project Root)

Project root: `/Users/tylarkin/Desktop/AI Cnntent Creator workflow/`

```
vlm_command_center.py       Main dashboard (port 8503)
office_server.py            Visual office server (port 5001)
execution/                  All deterministic Python scripts
directives/                 SOPs + knowledge docs (this file lives here)
.tmp/                       All live data files (leads, logs, sessions)
output/users/               Generated content for Neo/Shay/Tyrie
.env                        API keys + credentials
```

**Key data files in `.tmp/`:**
- `leads.json` — full outreach pipeline state
- `outreach_log.json` — email send history
- `activity_log.json` — Instagram post activity
- `approved_posts.json` — content queue (Neo + Shay)
- `tyrie_approved.json` — Ty's content queue
- `reply_drafts/` — pending reply drafts from Gmail

**Always use:** `/opt/homebrew/bin/python3.11` and `/usr/bin/git`

---

## Current Status Snapshot (Apr 2026)

- **Instagram:** All 3 accounts live and posting. Neo session needs a fresh login.
- **Outreach:** 30 leads sourced (10 per vertical), 0 with verified email (Explorium API credits depleted — need CSV export flow). Drip ready to run once emails are populated.
- **Websites:** Both live on Vercel with custom domains and video heroes.
- **Revenue:** $0 MRR — first clients not yet closed. Month 1 goal: 2–3 B2B clients at $1,500/mo.
- **Next unlock:** Get emails into leads.json → run first outreach batch → book first sales calls.

---

## CEO Decision Framework

The CEO agent should use this brief to answer questions like:

- **"What's the most important thing right now?"** → Get emails into the outreach pipeline and fire the first batch.
- **"Should we pitch X client at $997?"** → No. Anchor at $1,500–3,000. $997 is the floor after negotiation.
- **"Can we add a new vertical?"** → Only after current 3 verticals have case studies.
- **"Should we build X new feature?"** → Only if it directly unlocks revenue or solves a live client problem.
- **"What's blocking growth?"** → Lead email enrichment + first 2–3 B2B client closes.
