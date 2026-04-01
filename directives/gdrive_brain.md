# Directive: Google Drive Master Brain

## Purpose
Upload and maintain a structured Google Drive folder ("CreateFlow — Master Brain") housing all project strategy, training, enterprise, and outreach documents. This folder serves as the shared knowledge base accessible to Claude, Perplexity, and any connected web tools.

## Folder Structure
```
CreateFlow — Master Brain/
├── 01. Strategy/          — SaaS spec, agent action plans, SOP guides
├── 02. Enterprise & Offers/  — Instructor docs, offer stacks
├── 03. Training & Education/ — Step-by-step guides, bootcamp outlines
└── 04. Sales & Outreach/     — DM systems, prospecting docs
```

## Tool
`execution/upload_to_gdrive.py`

## First-Time Setup (one-time, ~5 minutes)
1. Go to console.cloud.google.com
2. Create a new project (e.g. "CreateFlow Brain")
3. Enable the **Google Drive API** (APIs & Services → Library → search "Drive")
4. Go to APIs & Services → Credentials → Create Credentials → **OAuth 2.0 Client ID**
5. Application type: **Desktop App** → name it anything → click Create
6. Click **Download JSON** → rename file to `credentials.json`
7. Place `credentials.json` in the project root (`AI Cnntent Creator workflow/`)
8. Run the script once — browser will open for Google sign-in authorization
9. `token.json` is auto-saved — no browser needed for future runs

## Running
```bash
cd "AI Cnntent Creator workflow"
.venv/bin/python execution/upload_to_gdrive.py
```

## Adding New Documents
1. Add the local file path to the appropriate subfolder entry in `UPLOAD_MANIFEST` inside the script
2. Re-run the script — it skips files already uploaded, only adds new ones

## Sharing for AI Tool Access
- **Claude.ai (browser):** Chat bar → Drive icon → Connect → navigate to "CreateFlow — Master Brain"
- **Perplexity:** Right-click folder in Drive → Share → "Anyone with the link" → paste link in chat
- **Future automation:** Script can be extended to watch a folder and auto-upload new files

## Credentials Note
- `credentials.json` and `token.json` are in `.gitignore` — never committed
- If token expires, the script auto-refreshes it silently
- If refresh fails, delete `token.json` and re-run to re-authorize
