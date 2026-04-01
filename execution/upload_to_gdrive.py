# execution/upload_to_gdrive.py
# Authenticates with Google Drive via OAuth and uploads project docs
# into a structured "CreateFlow — Master Brain" folder.
#
# FIRST-TIME SETUP:
#   1. Go to console.cloud.google.com
#   2. Create a project → Enable "Google Drive API"
#   3. Go to APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
#   4. Application type: Desktop App
#   5. Download JSON → save as "credentials.json" in the project root
#   6. Run this script — a browser window will open once for authorization
#   7. token.json is saved automatically for all future runs (no browser needed again)

import os
import json
import mimetypes
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ── Config ────────────────────────────────────────────────────────────────────

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Paths (relative to project root — run this script from there)
CREDENTIALS_PATH = "credentials.json"
TOKEN_PATH = "token.json"

# Root Drive folder name
ROOT_FOLDER_NAME = "CreateFlow — Master Brain"

# Files to upload: { "Drive subfolder": [list of absolute local paths] }
DOWNLOADS = os.path.expanduser("~/Downloads")

UPLOAD_MANIFEST = {
    "01. Strategy": [
        os.path.join(DOWNLOADS, "createflow_saas_spec_sheet.md"),
        os.path.join(DOWNLOADS, "agent_action_plans.md"),
        os.path.join(DOWNLOADS, "perplexity_claude_action_plan.md"),
        os.path.join(DOWNLOADS, "createflow_agent_sop.md"),
        os.path.join(DOWNLOADS, "# What is CreateFlow.docx"),
        os.path.join(DOWNLOADS, "task.md"),
    ],
    "02. Enterprise & Offers": [
        os.path.join(DOWNLOADS, "CREATEFLOW — INSTRUCTOR FOUNDATION DOCUMENT.docx"),
        os.path.join(DOWNLOADS, "VIRAL LENSE MEDIA Offer Stack .docx"),
    ],
    "03. Training & Education": [
        os.path.join(DOWNLOADS, "📖 Guide to AI Image Prompting.docx"),
        os.path.join(DOWNLOADS, "Step 1 Creating an AI Influencer Using Create Flow.docx"),
        os.path.join(DOWNLOADS, "Step 2 Creating an AI Character and Scene Using CreateFlow.docx"),
        os.path.join(DOWNLOADS, "Step 3 Creating a Character World Using Nano Banana Pro.docx"),
        os.path.join(DOWNLOADS, "Step 4 Creating a Mini-Series Using CreateFlow.docx"),
        os.path.join(DOWNLOADS, "VLM BOOTCAMP LESSON OUTLINE.docx"),
        os.path.join(DOWNLOADS, "VLM BOOTCAMP LESSON OUTLINE (1).docx"),
    ],
    "04. Sales & Outreach": [
        os.path.join(DOWNLOADS, "VLM_Prospecting_DM_System.docx"),
    ],
}

# ── Auth ──────────────────────────────────────────────────────────────────────

def authenticate():
    """Handles OAuth flow. Opens browser on first run, uses cached token after."""
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing access token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                print(f"❌ credentials.json not found at: {os.path.abspath(CREDENTIALS_PATH)}")
                print("   See script header for setup instructions.")
                raise FileNotFoundError("credentials.json missing")
            print("🌐 Opening browser for Google authorization (one-time only)...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
        print(f"✅ Token saved to {TOKEN_PATH}")

    return creds

# ── Drive Helpers ─────────────────────────────────────────────────────────────

def get_or_create_folder(service, name, parent_id=None):
    """Returns folder ID — creates it if it doesn't already exist."""
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    if files:
        print(f"   📁 Found existing folder: {name}")
        return files[0]["id"]

    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]

    folder = service.files().create(body=metadata, fields="id").execute()
    print(f"   📁 Created folder: {name}")
    return folder["id"]


def file_exists_in_folder(service, filename, folder_id):
    """Returns file ID if a file with this name already exists in the folder."""
    query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    return files[0]["id"] if files else None


def upload_file(service, local_path, folder_id):
    """Uploads a file to the given Drive folder. Skips if already present."""
    filename = os.path.basename(local_path)

    if not os.path.exists(local_path):
        print(f"   ⚠️  Skipping (not found locally): {filename}")
        return

    existing_id = file_exists_in_folder(service, filename, folder_id)
    if existing_id:
        print(f"   ⏭️  Already exists, skipping: {filename}")
        return

    mime_type, _ = mimetypes.guess_type(local_path)
    mime_type = mime_type or "application/octet-stream"

    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
    metadata = {"name": filename, "parents": [folder_id]}

    service.files().create(
        body=metadata,
        media_body=media,
        fields="id"
    ).execute()

    print(f"   ✅ Uploaded: {filename}")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("🔐 Authenticating with Google Drive...")
    creds = authenticate()
    service = build("drive", "v3", credentials=creds)

    print(f"\n📂 Setting up root folder: '{ROOT_FOLDER_NAME}'")
    root_id = get_or_create_folder(service, ROOT_FOLDER_NAME)

    total_uploaded = 0
    total_skipped = 0

    for subfolder_name, file_paths in UPLOAD_MANIFEST.items():
        print(f"\n🗂  {subfolder_name}")
        sub_id = get_or_create_folder(service, subfolder_name, parent_id=root_id)

        for path in file_paths:
            filename = os.path.basename(path)
            if not os.path.exists(path):
                print(f"   ⚠️  Skipping (not found): {filename}")
                total_skipped += 1
            elif file_exists_in_folder(service, filename, sub_id):
                print(f"   ⏭️  Already exists: {filename}")
                total_skipped += 1
            else:
                upload_file(service, path, sub_id)
                total_uploaded += 1

    print(f"\n{'─'*50}")
    print(f"✅ Done! {total_uploaded} uploaded, {total_skipped} skipped.")
    print(f"📎 Find your folder in Google Drive: '{ROOT_FOLDER_NAME}'")
    print(f"💡 Tip: Right-click the folder → Share → set to 'Anyone with the link' for Perplexity access.")


if __name__ == "__main__":
    main()
