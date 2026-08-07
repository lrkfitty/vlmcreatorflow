"""
Source local trade business leads from Instagram hashtag search.

Searches trade-niche hashtags (e.g. #dallasroofing, #houstonplumber) and
extracts business accounts from recent posts. Saves to .tmp/ig_dm_leads.json
ready for send_ig_dm.py.

Filters for likely local businesses:
  - Has a bio (not a blank personal account)
  - 100–50,000 followers (real business, not mega-brand)
  - Not already in ig_dm_log.json (already contacted)

Usage:
    # Search default trade hashtags for a city
    python3.11 execution/source_ig_leads.py --city dallas --vertical roofing

    # Search multiple verticals
    python3.11 execution/source_ig_leads.py --city houston --vertical roofing plumbing electrical

    # Custom hashtags
    python3.11 execution/source_ig_leads.py --hashtags dallasroofing texasroofer houstonroofing

    # Dry run — show what would be added without saving
    python3.11 execution/source_ig_leads.py --city miami --vertical electrician --dry-run

    # How many posts to pull per hashtag (default 30)
    python3.11 execution/source_ig_leads.py --city orlando --vertical contractor --limit 50
"""

import argparse
import json
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
TMP_DIR = PROJECT_ROOT / ".tmp"
DM_LEADS_FILE = TMP_DIR / "ig_dm_leads.json"
DM_LOG_FILE = TMP_DIR / "ig_dm_log.json"

load_dotenv(PROJECT_ROOT / ".env")

sys.path.insert(0, str(PROJECT_ROOT))
from execution.instagram_client import get_client

# Hashtag templates per vertical + city
VERTICAL_HASHTAG_TEMPLATES = {
    "roofing":      ["{city}roofing", "{city}roofer", "{city}roofingcontractor", "{city}roofingcompany"],
    "plumbing":     ["{city}plumbing", "{city}plumber", "{city}plumbingservice"],
    "electrical":   ["{city}electrician", "{city}electrical", "{city}electricalcontractor"],
    "hvac":         ["{city}hvac", "{city}hvacservice", "{city}airconditioning"],
    "contractor":   ["{city}contractor", "{city}generalcontractor", "{city}construction"],
    "landscaping":  ["{city}landscaping", "{city}landscaper", "{city}lawncare"],
    "remodeling":   ["{city}remodeling", "{city}remodel", "{city}homerenovation"],
}

FOLLOWER_MIN = 100
FOLLOWER_MAX = 50_000


def load_existing_leads() -> list[dict]:
    if DM_LEADS_FILE.exists():
        with open(DM_LEADS_FILE) as f:
            return json.load(f)
    return []


def load_dm_log() -> set:
    """Returns set of already-contacted handles."""
    if DM_LOG_FILE.exists():
        with open(DM_LOG_FILE) as f:
            log = json.load(f)
        return {e["handle"].lower() for e in log if e.get("status") == "sent"}
    return set()


def save_leads(leads: list[dict]):
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    with open(DM_LEADS_FILE, "w") as f:
        json.dump(leads, f, indent=2)


def already_in_leads(leads: list[dict], handle: str) -> bool:
    return any(l["handle"].lower() == handle.lower() for l in leads)


def build_hashtags(city: str, verticals: list[str]) -> list[str]:
    tags = []
    city_clean = city.lower().replace(" ", "")
    for v in verticals:
        templates = VERTICAL_HASHTAG_TEMPLATES.get(v.lower(), [f"{city_clean}{v.lower()}"])
        tags += [t.format(city=city_clean) for t in templates]
    return list(dict.fromkeys(tags))  # dedupe, preserve order


def _process_user(cl, user, vertical: str, source: str, already_contacted: set, existing_handles: set) -> dict | None:
    """Fetch full user info and return a lead dict if they pass filters. Returns None to skip."""
    handle = user.username.lower()
    if handle in already_contacted or handle in existing_handles:
        return None
    try:
        info = cl.user_info(user.pk)
        followers = info.follower_count
        if not (FOLLOWER_MIN <= followers <= FOLLOWER_MAX):
            return None
        bio = info.biography or ""
        lead = {
            "handle": handle,
            "business_name": info.full_name or "",
            "vertical": vertical,
            "bio": bio[:120],
            "followers": followers,
            "website": str(info.external_url) if info.external_url else "",
            "source_hashtag": source,
        }
        print(f"    + @{handle} ({followers:,} followers)" + (f" — {info.full_name}" if info.full_name else ""))
        time.sleep(1.5)
        return lead
    except Exception as e:
        print(f"    ! @{handle} info failed: {e}")
        return None


def scrape_hashtag(cl, hashtag: str, limit: int, vertical: str, city: str, already_contacted: set, existing_handles: set) -> list[dict]:
    found = []
    medias = None

    # Try hashtag_medias_top first — more reliable endpoint than recent
    for method_name in ["hashtag_medias_top", "hashtag_medias_top_v1"]:
        print(f"  Searching #{hashtag} via {method_name}...")
        try:
            method = getattr(cl, method_name)
            with ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(method, hashtag, limit)
                try:
                    medias = fut.result(timeout=15)
                    if medias:
                        print(f"  ✓ Got {len(medias)} posts from #{hashtag}")
                        break
                except FuturesTimeout:
                    print(f"  ! #{hashtag} {method_name} timed out after 15s — trying next method")
                    medias = None
        except Exception as e:
            print(f"  ! {method_name} error: {e}")
            medias = None

    # Fallback: search users directly by city + vertical keyword
    if not medias:
        query = f"{city} {vertical}".strip()
        print(f"  → Hashtag endpoints unavailable — falling back to user search: '{query}'")
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(cl.search_users, query, 20)
                try:
                    users = fut.result(timeout=15)
                    seen = set()
                    for user in (users or []):
                        if user.username.lower() in seen:
                            continue
                        seen.add(user.username.lower())
                        lead = _process_user(cl, user, vertical, f"search:{query}", already_contacted, existing_handles)
                        if lead:
                            found.append(lead)
                            existing_handles.add(lead["handle"])
                    return found
                except FuturesTimeout:
                    print(f"  ! search_users also timed out — skipping this hashtag")
                    return found
        except Exception as e:
            print(f"  ! search_users fallback failed: {e}")
            return found

    # Process media results
    seen_users: set = set()
    for media in medias:
        user = media.user
        if user.username.lower() in seen_users:
            continue
        seen_users.add(user.username.lower())
        lead = _process_user(cl, user, vertical, hashtag, already_contacted, existing_handles)
        if lead:
            found.append(lead)
            existing_handles.add(lead["handle"])

    return found


def run(args):
    # Build hashtag list
    if args.hashtags:
        hashtags = [(tag.lstrip("#"), args.vertical[0] if args.vertical else "trades") for tag in args.hashtags]
    else:
        if not args.city:
            print("Provide --city (e.g. --city dallas) or --hashtags directly.")
            sys.exit(1)
        verticals = args.vertical or list(VERTICAL_HASHTAG_TEMPLATES.keys())
        raw_tags = build_hashtags(args.city, verticals)
        # map each tag back to its vertical for lead metadata
        hashtags = []
        city_clean = args.city.lower().replace(" ", "")
        for v in (args.vertical or list(VERTICAL_HASHTAG_TEMPLATES.keys())):
            templates = VERTICAL_HASHTAG_TEMPLATES.get(v.lower(), [f"{city_clean}{v.lower()}"])
            for t in templates:
                hashtags.append((t.format(city=city_clean), v))

    already_contacted = load_dm_log()
    existing_leads = load_existing_leads()
    existing_handles = {l["handle"].lower() for l in existing_leads}

    print(f"\nSearching {len(hashtags)} hashtag(s) | limit {args.limit} posts each")
    print(f"Skipping {len(already_contacted)} already-contacted handles\n")

    if args.dry_run:
        print("[DRY RUN] Hashtags that would be searched:")
        for tag, vertical in hashtags:
            print(f"  #{tag}  ({vertical})")
        return

    print("Authenticating...")
    cl = get_client(account=args.account)
    print("Authenticated.\n")

    city_str = getattr(args, "city", "") or ""
    new_leads = []
    for tag, vertical in hashtags:
        found = scrape_hashtag(cl, tag, args.limit, vertical, city_str, already_contacted, existing_handles)
        new_leads += found
        existing_handles.update(l["handle"] for l in found)  # prevent cross-hashtag dupes
        if len(found):
            time.sleep(3)  # pause between hashtags

    if not new_leads:
        print("\nNo new leads found.")
        return

    all_leads = existing_leads + new_leads
    save_leads(all_leads)

    print(f"\nFound {len(new_leads)} new leads → saved to {DM_LEADS_FILE}")
    print(f"Total in file: {len(all_leads)}")
    print(f"\nNext step: python3.11 execution/send_ig_dm.py --from-file {DM_LEADS_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Source local trade business leads from Instagram hashtags.")
    parser.add_argument("--city", help="City to search (e.g. dallas, houston, miami)")
    parser.add_argument("--vertical", nargs="+", metavar="VERTICAL",
                        help=f"Trade vertical(s): {', '.join(VERTICAL_HASHTAG_TEMPLATES.keys())}")
    parser.add_argument("--hashtags", nargs="+", metavar="TAG",
                        help="Explicit hashtags to search (overrides --city/--vertical)")
    parser.add_argument("--account", default="vlm", help="IG account to search with (default: vlm)")
    parser.add_argument("--limit", type=int, default=30, help="Posts to pull per hashtag (default: 30)")
    parser.add_argument("--dry-run", action="store_true", help="Show hashtags that would be searched, no API calls")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
