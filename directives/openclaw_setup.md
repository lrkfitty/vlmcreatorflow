# OpenClaw Setup Directive

**Purpose:** Install OpenClaw locally on your Mac, wire it to Claude (via Anthropic API) as the LLM brain, add Perplexity as a research skill, and connect it to your CreateFlow repo so you can command it from your phone (Telegram/WhatsApp).

**Result:** You send one message on Telegram → OpenClaw reads your directives → calls Perplexity → tells Claude → runs your execution scripts → done. Hands-free.

---

## Part 1: Prerequisites

Before running anything, make sure you have:

| Requirement | How to check |
|---|---|
| macOS Ventura 13+ | Apple menu → About This Mac |
| Node.js 22+ | Run `node --version` in Terminal |
| Anthropic API key | [console.anthropic.com](https://console.anthropic.com) → API Keys |
| Perplexity API key | [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api) |
| Telegram account | Download Telegram on your phone |

**If Node.js is missing**, the OpenClaw installer handles it automatically. Don't stress it.

---

## Part 2: Install OpenClaw

### Step 1 — Run the one-line installer

Open Terminal and run:

```bash
curl -fsSL https://openclaw.ai/install.sh | sh
```

The script will:
- Detect your Mac hardware (Apple Silicon or Intel)
- Install Node.js 22+ if needed
- Install `openclaw` via npm globally
- Launch the first-time onboarding wizard

### Step 2 — Onboarding wizard

The wizard will ask you to choose your LLM. **Select Claude (Anthropic).**

Paste your Anthropic API key when prompted.

```
> Which AI provider would you like to use?
  → Claude (Anthropic)  ← pick this

> Enter your Anthropic API key:
  → sk-ant-xxxxxxxxxxxxx
```

### Step 3 — Connect a messaging channel (Telegram recommended)

The wizard will then ask which channel to connect. **Choose Telegram.**

Follow the on-screen steps to create a Telegram Bot via `@BotFather` and paste the bot token. This takes ~2 minutes.

After this, **you can message your OpenClaw agent from your phone.**

### Step 4 — Verify it's running

```bash
openclaw status
```

You should see: `✅ Agent online — Claude (claude-3-5-sonnet) — Telegram connected`

---

## Part 3: Add Perplexity as a Research Skill

OpenClaw uses a "Skills" system for external integrations. Perplexity connects via their MCP Server.

### Step 1 — Add the Perplexity MCP skill

```bash
openclaw skills add perplexity
```

When prompted, paste your Perplexity API key.

### Step 2 — Test it

Send this message to your OpenClaw bot on Telegram:

```
search perplexity: What are the top 5 pain points ad agencies have with stock photography costs in 2025?
```

OpenClaw will call Perplexity, return the answer directly in Telegram, and save it to memory.

---

## Part 4: Point OpenClaw at Your CreateFlow Repo

This lets OpenClaw read your directives and run your execution scripts autonomously.

### Step 1 — Set your project root

```bash
openclaw config set project_root "/Users/tylarkin/Desktop/AI Cnntent Creator workflow"
```

### Step 2 — Set directive path

```bash
openclaw config set directives_path "/Users/tylarkin/Desktop/AI Cnntent Creator workflow/directives"
```

### Step 3 — Test repo access

Send this to your Telegram bot:

```
read directive: lead_generation
```

OpenClaw will locate `directives/lead_generation.md` (or whatever directive you name) and confirm it can read it.

---

## Part 5: ClaudeClaw — Wire OpenClaw to Claude Code

ClaudeClaw makes OpenClaw use Claude Code as its execution backend, meaning it can directly write and run code in your repo.

### Step 1 — Install Claude Code (if not already installed)

```bash
npm install -g @anthropic-ai/claude-code
```

### Step 2 — Enable ClaudeClaw mode in OpenClaw

```bash
openclaw config set backend claude-code
openclaw config set claude_code_path "/Users/tylarkin/Desktop/AI Cnntent Creator workflow"
```

### Step 3 — Test it end-to-end

Send this to Telegram:

```
using the createflow repo, tell me what execution scripts exist in the execution/ folder
```

OpenClaw will invoke Claude Code, which will read your repo and return a list of your Python scripts.

---

## Part 6: What to Tell Claude Code

Once ClaudeClaw is wired up, here are the exact prompts to use **inside Claude Code** (terminal or Telegram via OpenClaw) to integrate everything:

### Prompt 1 — Introduce the architecture
```
Read the file at directives/openclaw_setup.md. This project uses a 3-layer architecture:
Layer 1 = directives/ (SOPs), Layer 2 = you as orchestrator, Layer 3 = execution/ (Python scripts).
Your job is to read directives, call execution scripts, and report results.
Do not write ad-hoc code — always check execution/ first.
```

### Prompt 2 — Wire Perplexity research into a script
```
Check execution/ for any existing research or scraping scripts.
If none exist, create execution/perplexity_research.py that:
- Accepts a research query as a command-line argument
- Calls the Perplexity API (key in .env as PERPLEXITY_API_KEY)
- Returns a clean markdown summary saved to .tmp/research_output.md
- Is well-commented and handles API errors gracefully
```

### Prompt 3 — Lead generation pipeline
```
Read directives/lead_generation.md (if it exists) or the saas spec sheet for context.
Check execution/ for a lead scraping script.
If none exists, create execution/scrape_leads.py that:
- Takes a niche (e.g. "ad agencies") and location as arguments
- Uses the Perplexity API to research and compile a list of 20 companies
- Outputs to .tmp/leads_<niche>.csv with columns: company, contact_name, email_guess, pain_point
```

### Prompt 4 — Cold email draft
```
Read .tmp/leads_<niche>.csv and the saas spec sheet at
'/Users/tylarkin/Downloads/VLM AGENT FILES/createflow_saas_spec_sheet.md'.
Using the Escape-to-Arrival framework from Section 3, draft 3 cold email variations
targeting this niche. Save them to .tmp/cold_emails_<niche>.md.
```

---

## Daily Workflow (Once Set Up)

You are now the conductor, not the worker. Here's your 3-message daily ops loop via Telegram:

```
1. "Research: [topic or niche]"
   → OpenClaw calls Perplexity → saves to .tmp/

2. "Build: [feature or task]"
   → OpenClaw invokes Claude Code → writes/runs code in your repo

3. "Draft: [email/copy/directive]"
   → Claude writes the asset → saves to .tmp/ or Google Drive
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `openclaw: command not found` | Run `npm install -g openclaw` manually |
| Claude returns wrong model | Run `openclaw config set model claude-3-5-sonnet-20241022` |
| Telegram bot not responding | Re-run `openclaw channels setup telegram` |
| Perplexity skill not found | Run `openclaw skills list` to confirm it installed |
| Project root not reading | Double-check path with `openclaw config get project_root` |

---

## Keys Needed (add to `.env`)

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxx
```

These are already the right location — your `.env` file in the project root.
