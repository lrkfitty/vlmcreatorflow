#!/usr/bin/env python3
"""
source_local_leads.py — Scrape local business leads from Google Maps (Places API New).
Targeting businesses WITHOUT a website, with 5+ reviews, and a phone number.

Usage:
    python3 execution/source_local_leads.py --city "Dallas" --vertical "roofing contractor"
    
Outputs:
    .tmp/local_leads.json
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
TMP_DIR  = BASE_DIR / ".tmp"
TMP_DIR.mkdir(exist_ok=True)
LEADS_FILE = TMP_DIR / "local_leads.json"

env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

def load_existing_leads():
    if not LEADS_FILE.exists():
        return []
    with open(LEADS_FILE) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_leads(leads):
    with open(LEADS_FILE, "w") as f:
        json.dump(leads, f, indent=2)

def search_places_new(query):
    print(f"Searching Google Places (New) for: '{query}'...")
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.websiteUri,places.nationalPhoneNumber,places.rating,places.userRatingCount,places.googleMapsUri,nextPageToken",
        "Content-Type": "application/json"
    }
    
    all_places = []
    page_token = None
    
    import time
    for _ in range(3): # Grab up to 3 pages (60 results max per query)
        data = {
            "textQuery": query,
            "pageSize": 20
        }
        if page_token:
            data["pageToken"] = page_token
            
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        resp_data = resp.json()
        
        places = resp_data.get("places", [])
        if not places:
            break
            
        all_places.extend(places)
        
        page_token = resp_data.get("nextPageToken")
        if not page_token:
            break
            
        time.sleep(1) # delay between paginated requests
            
    return all_places

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", required=True, help="City to search in (e.g. 'Surprise')")
    parser.add_argument("--vertical", required=True, help="Business type (e.g. 'roofing contractor')")
    args = parser.parse_args()

    if not GOOGLE_API_KEY:
        print("ERROR: GOOGLE_API_KEY not found in environment.")
        sys.exit(1)

    query = f"{args.city} {args.vertical}"
    results = search_places_new(query)
    
    if not results:
        print("No results found.")
        sys.exit(0)
        
    print(f"Found {len(results)} places. Filtering for leads without websites...")
    
    existing_leads = load_existing_leads()
    existing_names = {lead.get("business_name", "").lower() for lead in existing_leads}
    
    new_leads = []
    
    for place in results:
        name = place.get("displayName", {}).get("text", "")
        if not name:
            continue
            
        if name.lower() in existing_names:
            print(f"  SKIP: {name} (Already in local_leads.json)")
            continue
            
        website = place.get("websiteUri")
        if website:
            print(f"  SKIP: {name} (Has a website: {website})")
            continue
            
        reviews = place.get("userRatingCount", 0)
        if reviews < 5:
            print(f"  SKIP: {name} (Only {reviews} reviews, need 5+)")
            continue
            
        phone = place.get("nationalPhoneNumber")
        if not phone:
            print(f"  SKIP: {name} (No phone number listed)")
            continue
            
        # Qualifies!
        lead = {
            "business_name": name,
            "owner_name": "",
            "phone": phone,
            "city": args.city,
            "vertical": args.vertical,
            "google_maps_url": place.get("googleMapsUri", ""),
            "website": None,
            "status": "prospect",
            "site_built": False,
            "contacted": False,
            "notes": f"Rating: {place.get('rating')} ({reviews} reviews)"
        }
        
        new_leads.append(lead)
        existing_names.add(name.lower())
        print(f"  ★ QUALIFIED: {name} | {phone} | {reviews} reviews")
        
    if new_leads:
        existing_leads.extend(new_leads)
        save_leads(existing_leads)
        print(f"\nAdded {len(new_leads)} new qualified leads to {LEADS_FILE}")
    else:
        print("\nNo new qualified leads found matching the criteria (no website, 5+ reviews, has phone).")
        print("Try a different city or vertical.")

if __name__ == "__main__":
    main()
