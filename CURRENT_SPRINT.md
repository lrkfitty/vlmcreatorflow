# CURRENT SPRINT — VLM / CreateFlow
> **This file is the shared handoff between Gemini (Antigravity) and Claude Code.**
> Whichever AI you're currently working with MUST read this first and update it when the session ends.
> Last updated: 2026-04-19 — Claude Code session

---

## 🔴 Active Focus: Scaling the Local Business Website Service (B2B)

### What Was Decided This Session (Apr 19, 2026)

Ty is doubling down on the **Local Business Website Service** and has completely revamped the VLM Instagram (@virallensemediavlm) to act as a **B2B Landing Page**. 

The strategy is now live: VLM creates a 9-post "niche grid", where the entire AI cast (Tyrie, Angeil, Neo, Frannie, Shay, Jazmine, Sophia) act as successful owners/CEOs of various trade niches (Roofing, Construction, Plumbing, Remodeling, Landscaping, Electrical). 

This sells the *transformation* visually.

**Pricing Setup (Locked In):**
- Web Presence: $1,000 setup + $297/mo
- Full Bundle: $2,000 setup + $1,500/mo
*CTA across all platforms is always: "DM 'BUILD' for a free custom website mockup."*

---

## ✅ DONE

| Task | Notes |
|------|-------|
| VLM Instagram Overhaul | The @virallensemediavlm account has been fully converted to a B2B feed. |
| B2B Content Generator | Created `execution/vlm_roofing_batch.py` which pushes out a 9-post B2B specific grid. All 9 initial posts have been generated. |
| Auto-poster Integration | `execution/auto_poster.py` was updated to support `--account vlm` alongside Neo, Shay, and Tyrie. Posts from `output/users/VLM/Instagram/` if approved in `.tmp/approved_posts.json`. |
| VLM Reviewer Dashboard | Created `vlm_reviewer.py` — a standalone HTTP reviewer UI (port 7860) where you can Approve, Reject, Regenerate, or instantly Post VLM content. No more manual JSON editing required. |
| VLM Credentials Setup | `IG_USERNAME_VLM`, `IG_PASSWORD_VLM`, and a fresh `IG_SESSIONID_VLM` have been injected into `.env`. First posts are successfully live. |
| Mirror files synced | `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, and `ceo_agent_brief.md` synced with VLM context. |
| Construction website template | (Prior pass) `templates/construction_site/index.html` built against Medina Brothers Roofing Co. |
| Enterprise site — Local Trades vertical | Added 4th vertical card (Local Trades & Construction) with "DM 'BUILD'" CTA copy. `vlm-enterprise/index.html` |
| Enterprise site — Local biz pricing section | Added two new pricing cards below agency tiers: $1,000 setup/$297mo (Web Presence) + $2,000/$1,500mo (Full Bundle). |
| Enterprise site — Setup fee fix | Pricing card 1 was blank — now reads "Included in Month 1". |
| Enterprise site — Proof accounts updated | Added @virallensemediavlm and @tytheguyyttg to proof section. Now 4 accounts displayed in 2×2 grid. |
| Enterprise site — ?book=1 handler | JS now auto-scrolls to booking form when URL contains `?book=1` — outreach email deep-links now work. |
| Enterprise site deployed | Pushed to `lrkfitty/vlm-enterprise` main. Vercel auto-deployed to `enterprise.vlmcreateflow.com`. |

---

## 🟡 What Still Needs to Be Built

### Priority 1 — Connect the Outreach to the VLM feed
Now that the VLM Instagram is a stunning B2B portfolio, cold outreach needs to explicitly drive traffic to the Instagram page alongside the preview website. 
- **Status:** NOT STARTED
- **Claude's task:** Revise the cold outreach templates/scripts to highlight the new VLM Instagram proof and the new local biz pricing. Add `?book=1` deep-link to outreach emails (handler is now live on the enterprise site).

### Priority 2 — Pipeline Tracker + Follow Up
Since VLM is asking prospects to "DM 'BUILD'", there needs to be an automated way to track these inbound responses, alongside the existing outbound responses.
- **Status:** NOT STARTED
- **Claude's task:** Hook up a simple CRM pipeline (Google Sheets or Streamlit dashboard) that sweeps Instagram DMs or tracks status of DM conversations. 

### Priority 3 — Client Swap Automation Script
Ty has the HTML template with `<!-- SWAP: -->` comments. Claude should build a script that takes a URL / Google Maps link, scrapes the basics (name, phone, address, 2-3 images), and automatically generates the tailored HTML for the preview site.
- **Status:** NOT STARTED

---

## 🚧 Blockers

| Blocker | Detail |
|---------|--------|
| B2B outreach pipeline stalled | 0 verified leads — Vibe Prospecting API credits depleted. Fix: export manually from app.vibeprospecting.ai and run `source_leads.py --from-csv` |
| IG Session refreshing | Relying on long-lived session IDs works, but if VLM session dies, need to rerun login script. |

---

## 🟢 VLM Core — Status Snapshot

| Component | Status | Blocker |
|-----------|--------|---------|
| CreateFlow platform | ✅ Running | None |
| Instagram Poster (Neo/Shay/Ty/VLM) | ✅ Posting | All wired. VLM reviewer on port 7860 handles approvals. |
| B2B outreach pipeline | ⏸️ Built, idle | Needs CSV import fix due to API limit. |
| B2B website (b2b) | ✅ Live | None |
| Revenue | $0 MRR | Feed is live, ready to pitch. |

---

## 📝 Handoff Note — Claude Code (2026-04-19)

**What I did this session:**
- Full audit of `enterprise.vlmcreateflow.com` against the April 19 CEO brief update
- Updated enterprise site with: local trades vertical card, local biz pricing section ($297/mo + $1,500/mo tiers), 4 proof accounts, `?book=1` deep-link handler, setup fee fix
- Deployed — live on Vercel

**Instagram DM outreach discussion:**
- Ty asked about sending IG DMs to leads. Two options discussed:
  1. `agent-browser` skill (manual targeted outreach via browser session)
  2. Python script `execution/send_ig_dm.py` using instagrapi + VLM session file — bulk DMs from a handle list, cron-able
- **Warning:** IG rate-limits DM automation aggressively on new accounts. Max 20–30 DMs/day. This script has NOT been built yet.

**What still needs to happen:**
1. Build `execution/send_ig_dm.py` for IG DM outreach to local trade leads
2. Swap `b2b-1/2/3.jpg` proof images on enterprise site with new VLM niche grid images (once `vlm_roofing_batch.py` run is complete)
3. Update outreach email templates to reference @virallensemediavlm and use `?book=1` deep-link
4. Website Swap script (Priority 3 above) — still NOT STARTED

---

## 📋 How to Use This File

**When starting a session:**
1. Read this file top to bottom
2. Check "What Needs to Be Built" for active tasks
3. Pick up where it says NOT STARTED or IN PROGRESS

**When ending a session:**
1. Update task statuses (NOT STARTED → IN PROGRESS → DONE)
2. Add any new decisions made
3. Note any blockers discovered
4. Flag anything for the next AI to watch out for
