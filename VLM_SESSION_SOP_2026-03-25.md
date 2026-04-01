# VLM Session SOP — 2026-03-25
> Everything built, configured, and deployed in this session. Use as reference for rebuilding or onboarding.

---

## 1. Command Center

**File:** `vlm_command_center.py`
**Run:**
```bash
lsof -ti:8503 | xargs kill -9 2>/dev/null
/opt/homebrew/bin/python3.11 -m streamlit run vlm_command_center.py --server.port 8503
```
**URL:** http://localhost:8503
**Install streamlit if missing:** `/opt/homebrew/bin/pip3.11 install streamlit`

---

## 2. GitHub Setup

**Account:** `lrkfitty`
**Auth:** `gh auth login` → GitHub.com → HTTPS → browser

**4 repos pushed:**
| Repo | URL |
|------|-----|
| vlm-b2b | github.com/lrkfitty/vlm-b2b |
| vlm-b2c | github.com/lrkfitty/vlm-b2c |
| vlm-crm | github.com/lrkfitty/vlm-crm |
| funnel | github.com/lrkfitty/funnel |

**Push a repo:**
```bash
gh repo create lrkfitty/<repo> --public
/usr/bin/git -C "/Users/tylarkin/Desktop/AI Cnntent Creator workflow/<repo>" remote add origin https://github.com/lrkfitty/<repo>.git
/usr/bin/git -C "/Users/tylarkin/Desktop/AI Cnntent Creator workflow/<repo>" push -u origin main
```
Note: always use `/usr/bin/git` — bare `git` may not be in PATH.

---

## 3. Streamlit Cloud Deployment

**URL:** share.streamlit.io (sign in with GitHub → lrkfitty)

| App | Repo | Main File | Live URL |
|-----|------|-----------|----------|
| B2B | vlm-b2b | app.py | vlmforbusiness.streamlit.app |
| B2C | vlm-b2c | app.py | createnow.streamlit.app |
| CRM | vlm-crm | app.py | vlmcreator.streamlit.app |
| Funnel | funnel | Home.py | flowleads.streamlit.app |

**Secrets per app (Streamlit Cloud → Settings → Secrets):**

vlm-b2b:
```toml
SMTP_USER = "noreply@vlmcreateflow.com"
SMTP_PASS = "Vlmcreateflow1!"
STRIPE_SECRET_KEY = "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"
STRIPE_SUCCESS_URL = "https://vlmforbusiness.streamlit.app/?checkout=success"
STRIPE_CANCEL_URL = "https://vlmforbusiness.streamlit.app/?checkout=cancel"
```

vlm-b2c:
```toml
SMTP_USER = "noreply@vlmcreateflow.com"
SMTP_PASS = "Vlmcreateflow1!"
STRIPE_SECRET_KEY = "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"
STRIPE_SUCCESS_URL = "https://createnow.streamlit.app/?checkout=success"
STRIPE_CANCEL_URL = "https://createnow.streamlit.app/?checkout=cancel"
```

vlm-crm:
```toml
CRM_USERNAME = "admin"
CRM_PASSWORD = "VLM5BA2C052"
STRIPE_B2B_LINK = "https://buy.stripe.com/bJe28s3Ej9SX7XlgB78Vi08"
STRIPE_B2C_LINK = "https://buy.stripe.com/28E3cweiX2qv7Xl0C98Vi09"
```

funnel:
```toml
SMTP_USER = "noreply@vlmcreateflow.com"
SMTP_PASS = "Vlmcreateflow1!"
STRIPE_B2B_LINK = "https://buy.stripe.com/bJe28s3Ej9SX7XlgB78Vi08"
STRIPE_B2C_LINK = "https://buy.stripe.com/28E3cweiX2qv7Xl0C98Vi09"
```

---

## 4. Stripe

**Account:** Stripe dashboard (live mode)
**Secret key:** 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

**Price IDs:**
- B2B: `price_1TBzOvKIWXG1ZQJE9LYl49Ix` — $997/mo
- B2C: `price_1TBzOvKIWXG1ZQJEyhifAvgr` — $49/mo

**Payment links (generated via API):**
- B2B: `https://buy.stripe.com/bJe28s3Ej9SX7XlgB78Vi08`
- B2C: `https://buy.stripe.com/28E3cweiX2qv7Xl0C98Vi09`

**Generate new payment link:**
```bash
curl -s https://api.stripe.com/v1/payment_links \
  -u "sk_live_...:" \
  -d "line_items[0][price]=<price_id>" \
  -d "line_items[0][quantity]=1"
```

---

## 5. Domain & Email

**Domain:** `vlmcreateflow.com` (Namecheap, $11.28/yr)
**Email provider:** Namecheap Private Email ($6.48/mo after trial)
**SMTP server:** `mail.privateemail.com:587` (STARTTLS)

**Mailboxes:**
| Address | Password | Use |
|---------|----------|-----|
| noreply@vlmcreateflow.com | Vlmcreateflow1! | App notifications |
| hello@vlmcreateflow.com | Vlmcreateflow1! | Client-facing / cold outreach |
| tylarkin@vlmcreateflow.com | Larkin2017! | Receives lead notifications |

**DNS redirects (Namecheap Advanced DNS):**
| Host | Type | Target |
|------|------|--------|
| www | URL Redirect | https://flowleads.streamlit.app |
| b2b | URL Redirect | https://vlmforbusiness.streamlit.app |
| b2c | URL Redirect | https://createnow.streamlit.app |
| crm | URL Redirect | https://vlmcreator.streamlit.app |
| @ | URL Redirect | https://www.vlmcreateflow.com |

---

## 6. Instagram Auto-Poster

**Script:** `execution/auto_poster.py`
**Run manually:** `/opt/homebrew/bin/python3.11 execution/auto_poster.py --account all`
**Cron:** 10:00 and 22:00 Bangkok time (system crontab)
**Logs:** `.tmp/cron_post.log`, `.tmp/activity_log.json`

**Accounts:**
| Account | Handle | Content |
|---------|--------|---------|
| Neo | @neoismyname1 | Single images |
| Shay | @shay.so.fine | Carousels |
| Ty | @tytheguyyttg | Carousels |

**Key rule:** Never auto-generate content — only posts pre-approved content to avoid unexpected API costs.

---

## 7. Skills Saved

Two skills saved to `~/.claude/skills/` for future sessions:
- `/vlm-deploy` — full GitHub + Streamlit Cloud deployment workflow
- `/vlm-auto-poster` — Instagram posting system docs

---

## 8. Next Steps (as of session end)

- [ ] Vibe Prospecting integration — lead sourcing via app.vibeprospecting.ai
- [ ] Cold outreach sequences from hello@vlmcreateflow.com
- [ ] Migrate apps to Railway/Render for true custom domain support (when ready to scale)
- [ ] Wire hello@ for client onboarding emails
- [ ] Shay content generation — run `execution/shay_generate_remaining.py` to fill gaps
