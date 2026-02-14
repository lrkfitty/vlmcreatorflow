import streamlit as st
import sys
import os
import json
import time

# Add execution directory to path to import scripts
sys.path.append(os.path.join(os.path.dirname(__file__), 'execution'))

try:
    import importlib
    import load_assets as la_module
    importlib.reload(la_module)
    import load_assets as la_module
    importlib.reload(la_module)
    from load_assets import load_assets, promote_image_to_asset
    from execution.magic_ui import inject_magic_css, magic_text, card_begin, card_end, circular_progress, hover_button
    import generate_image as gi_module
    importlib.reload(gi_module)
    from generate_image import generate_image_from_prompt
    
    import generate_prompt as gp_module
    importlib.reload(gp_module)
    from generate_prompt import generate_prompt_content
    from campaign_runner import CampaignManager
    from execution.generate_video import generate_video_kling, generate_video_humo
    from execution.s3_uploader import upload_file_obj, delete_file
    from generate_video_prompt import generate_motion_prompt
    from world_manager import load_world_db, get_assets_by_category, get_scenarios
    from execution.kling_client import KlingClient
    from execution.sora_client import SoraClient
    from execution.series_processor import parse_script_to_scenes
    from execution.auth import auth_mgr
    from execution.character_utils import build_character_prompt, get_character_sheet_prompt
except ImportError as e:
    st.error(f"Error importing scripts: {e}")
    st.stop()

# --- REMOTE CONFIG INJECTION (Secrets -> Env) ---
# Ensure helper scripts can see secrets as env vars, handling nested tables (e.g. [env])
def recursive_secrets_load(secrets_obj, prefix=""):
    for key, val in secrets_obj.items():
        if isinstance(val, dict):
             # Recursively dive in. Prefix optional? 
             # Usually Streamlit users might group like [aws] bucket_name. 
             # We want to eventually find simple keys if they exist deep down.
             recursive_secrets_load(val, prefix)
        else:
            # Flatten: If key is not in env, add it.
            # We trust the deepest key (or outer?) - First come first serve or overwrite?
            # Let's overwrite to ensure secrets take precedence.
            # Note: We don't prefix because scripts expect "S3_BUCKET_NAME", not "aws_S3_BUCKET_NAME"
            if key not in os.environ:
                 os.environ[key] = str(val)

try:
    if hasattr(st, "secrets"):
         # Convert StreamlitSecrets to dict for recursion
         recursive_secrets_load(dict(st.secrets))
except Exception as e:
    # Safe to ignore locally
    pass

st.set_page_config(page_title="CreateFlow | Viral Lense Media", layout="wide", page_icon=None)

# DEBUG: Inject Diagnostics if requested or if path missing
if os.getenv("S3_BUCKET_NAME") is None and hasattr(st, "secrets"):
     # Auto-show diagnostics if we have secrets but S3 is missing (Misconfiguration)
     with st.sidebar.expander("🛠️ System Diagnosis (Auto)", expanded=True):
          st.error("S3 Bucket Not Found in Env")
          st.write("Secrets Keys Found:")
          def elem_keys(obj, d=0):
               if d > 2: return
               for k, v in obj.items():
                    st.write(f"{'-'*d} {k}")
                    if isinstance(v, dict): elem_keys(v, d+1)
          if hasattr(st, "secrets"):
               elem_keys(dict(st.secrets))
          else:
               st.write("No 'st.secrets' object.")

# --- AUTHENTICATION GATE MOVED AFTER THEME LOADING ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- THEME INJECTION ---
# --- THEME INJECTION ---
def apply_custom_theme():
    # Inject Magic UI styles
    inject_magic_css()

apply_custom_theme()

# --- NEW AUTHENTICATION UI (MULTI-USER) ---
# from execution.auth import auth_mgr (Moved to top)
import extra_streamlit_components as stx
import datetime

# Cookie Manager Init
cookie_manager = stx.CookieManager()

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Check Cookie
if not st.session_state.get("authenticated", False):
    try:
        # Check if user is trying to manually login (typing in form)
        # If so, SKIP auto-login to prevent overwriting their action
        manual_attempt = st.session_state.get("auth_user") or st.session_state.get("auth_pass") or st.session_state.get("reg_user")
        
        if not manual_attempt:
            auth_token = cookie_manager.get(cookie="auth_token")
            if auth_token:
                 user_payload = auth_mgr.verify_token(auth_token)
                 if user_payload:
                     st.session_state.authenticated = True
                     st.session_state.current_user = user_payload
    except Exception:
        pass

def handle_login():
    user = st.session_state.get("auth_user", "")
    pwd = st.session_state.get("auth_pass", "")
    
    token, msg = auth_mgr.login(user, pwd)
    
    if token:
        st.session_state.authenticated = True
        st.session_state.current_user = auth_mgr.verify_token(token)
        # Set Cookie (Expires in 7 days)
        cookie_manager.set("auth_token", token, expires_at=datetime.datetime.now() + datetime.timedelta(days=7))
    else:
        st.error(f"⛔ {msg}")

def handle_signup():
    new_user = st.session_state.get("reg_user", "")
    new_pass = st.session_state.get("reg_pass", "")
    
    if not new_user or not new_pass:
        st.error("Please fill in all fields.")
        return

    success, msg = auth_mgr.create_user(new_user, new_pass, role="viewer")
    
    if success:
        st.success("Account Created! Logging in...")
        # Auto Login
        token, _ = auth_mgr.login(new_user, new_pass)
        st.session_state.authenticated = True
        st.session_state.current_user = auth_mgr.verify_token(token)
        # Set Cookie
        cookie_manager.set("auth_token", token, expires_at=datetime.datetime.now() + datetime.timedelta(days=7))
    else:
        st.error(f"Error: {msg}")

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<div style='text-align: center; color: #64748B; font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;'>Welcome to an all new tool brought to you by</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; color: #1E293B; font-size: 1.8rem; font-weight: 900; letter-spacing: 0.1em; margin-bottom: 0px;'>VIRAL LENSE MEDIA</div>", unsafe_allow_html=True)
        # Magic Text H1
        magic_text("CreateFlow", type="h1")
        
        # Auth Tabs
        tab_login, tab_signup = st.tabs(["Login", "Create Account"])
        
        with tab_login:
            st.text_input("Username", key="auth_user", placeholder="admin")
            st.text_input("Password", type="password", key="auth_pass", on_change=handle_login, placeholder="Password")
            # Remember Me removed (Default behavior now)
            st.button("LOGIN", on_click=handle_login, use_container_width=True, type="primary")

        with tab_signup:
            st.text_input("New Username", key="reg_user")
            st.text_input("New Password", type="password", key="reg_pass")
            st.button("SIGN UP", on_click=handle_signup, use_container_width=True)
        
    st.stop()

# --- LOGOUT & SIDEBAR INFO ---
with st.sidebar:
    st.caption("v4.0.0 | Build: Aurora UI") 
    if st.session_state.get("authenticated"):
        u_info = st.session_state.get("current_user", {"username": "Ghost"})
        credits = auth_mgr.get_credits(u_info.get("username"))
        st.markdown(f"**{u_info.get('username')}** ({u_info.get('role', 'Viewer')})")
        c1, c2 = st.columns([3, 1])
        with c1:
             st.markdown(f"<span style='font-size: 1.5rem; font-weight: 700; color: #fff;'>Credits: {credits}</span>", unsafe_allow_html=True)
        with c2:
             if st.button("🔄", key="refresh_creds", help="Hard Refresh (Clear Cache)"):
                 st.cache_data.clear()
                 st.cache_resource.clear()
                 st.rerun()
        
        # Explicit Reset for Troubleshooting
        if st.button("⚠️ RESET SYSTEM CACHE", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Cache Cleared!")
            time.sleep(1)
            st.rerun()

        if st.button("Logout"):
            # Clear cookie by setting it with past expiration
            cookie_manager.set("auth_token", "", expires_at=datetime.datetime.now() - datetime.timedelta(days=1))
            # Fully clear session state to preventing lingering variables
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            # Allow time for cookie to clear on frontend
            with st.spinner("Logging out..."):
                time.sleep(1)
            st.rerun()
    st.divider()

# HEADER
# HEADER
st.markdown("<div class='brand-overline'>Viral Lense Media</div>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; font-size: 6rem; font-weight: 800; letter-spacing: -0.05em; margin-bottom: 0.5rem; text-shadow: 0 0 30px rgba(255,255,255,0.1);'>CreateFlow</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 1.2rem; margin-bottom: 3rem; letter-spacing: 0.2em; text-transform: uppercase;'>Enterprise-Grade Content Workflow</p>", unsafe_allow_html=True)

# Load Assets
user_asset_path = None
if st.session_state.get("authenticated"):
    username = st.session_state.current_user.get("username", "guest")
    user_asset_path = os.path.join("output", "users", username, "Assets")
    
    # Debug
    # Debug Info Removed for Cleanliness
    # if os.getenv("S3_BUCKET_NAME"):
    #     st.toast(f"Cloud Mode: {os.getenv('S3_BUCKET_NAME')}")

try:
    # V4.1: Cached Loading (Performance Fix)
    # V4.2: Split Caching (Ultra Performance)
    # 1. Base Assets (Persisted to Disk, Updates Hourly or Manual)
    @st.cache_data(ttl=3600, persist="disk", show_spinner="Loading Global Catalog...")
    def get_base_assets():
        return load_assets(user_assets_dir=None, skip_base=False)

    # 2. User Assets (Session Cache, Fast, Updates often)
    @st.cache_data(ttl=300, show_spinner=False)
    def get_user_assets(user_path):
        if not user_path: return {}
        return load_assets(user_assets_dir=user_path, skip_base=True)

    # Load & Merge
    base_assets = get_base_assets()
    user_assets_raw = get_user_assets(user_asset_path) if user_asset_path else {} # Return empty dict structure

    # Deep Merge (Naive update overwrites dicts, we need to merge keys within categories)
    # Actually load_assets returns {'characters': {...}, ...}
    # So we need to merge the inner dicts
    assets_raw = base_assets.copy() # Shallow copy of structure
    
    # Helper to merge deep
    # If user_assets_raw is just the dict structure
    # Wait, load_assets returns { 'characters': {}, ... }
    # So we iterate and update
    
    # Correction: If get_user_assets returns a full struct, we iterate keys
    # But wait, did I verify load_assets returns empty dicts for categories? Yes.
    
    # Safe Merging
    # We must deep copy the inner dicts first?
    # Actually, st.cache_data returns mutable refs? We should copy.
    import copy
    assets_raw = copy.deepcopy(base_assets) # Protect the disk cache
    
    if isinstance(user_assets_raw, dict):
        for cat, items in user_assets_raw.items():
            if cat in assets_raw and isinstance(items, dict):
                assets_raw[cat].update(items)
            elif cat not in assets_raw:
                 assets_raw[cat] = items
    
    # Proceed

    if "global_assets" not in st.session_state:
        st.session_state.global_assets = assets_raw

    # Alias for local scope simple access (Read Only)
    assets = st.session_state.global_assets
    
    # Debug
    # st.sidebar.write(f"User Assets Found: {len(assets.get('characters', {}))}")
    vibes_data = assets.get('vibes', {})
    outfits_data = assets.get('outfits', {})

    characters_data = assets.get('characters', {}).copy()
    
    # Merge Friends/Relations into Characters options
    relations_data = assets.get('relations', {})
    characters_data.update(relations_data)
    
    vibes_list = list(vibes_data.keys())
    outfits_list = list(outfits_data.keys())
    characters_list = list(characters_data.keys())
    
except Exception as e:
    st.error(f"Failed to load assets: {e}")
    st.stop()

# --- UI Inputs ---
# Load Knowledge Base
knowledge_base = {}
try:
    with open("knowledge_base.json", "r") as f:
        knowledge_base = json.load(f)
except FileNotFoundError:
    pass

# Initialize Campaign Manager
campaign_mgr = CampaignManager()

# Helper: Scan Models - DEPRECATED for Cloud

# --- TABS LAYOUT# TABS
# --- HELPER: FILE ISOLATION ---
def get_user_out_dir(category="General"):
    """Returns a user-isolated output path."""
    if st.session_state.get("authenticated"):
        username = st.session_state.current_user.get("username", "guest")
    else:
        username = "guest"
    
    # Path: output/users/{username}/{category}
    path = os.path.join("output", "users", username, category)
    os.makedirs(path, exist_ok=True)
    return path

# --- TABS LAYOUT ---
# --- TABS LAYOUT (Persistent) ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Workflow Wizard"

# Custom CSS for Pill-like Tabs
st.markdown("""
<style>
    div[data-testid="stRadio"] > label > div {
        display: none;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        flex-direction: row;
        justify-content: center;
        overflow-x: auto;
        padding-bottom: 10px;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        background-color: #f0f2f6;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin-right: 10px;
        border: 1px solid #e0e0e0;
        transition: all 0.2s;
        cursor: pointer;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ff4b4b;
        color: white;
        border-color: #ff4b4b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

nav_options = [
    "Workflow Wizard", 
    "My Gallery",
    "Asset Library",
    "Mini Series",
    "World Builder",
    "Campaign Queue", 
    "Video Studio",
    "Character Studio",
    "Multi-Shot Generator"
]

# Admin Panel visibility
if st.session_state.get("authenticated") and st.session_state.current_user.get("role") == "admin":
    nav_options.append("Admin Panel")

# Use a callback to update state immediately or just bind to key
selection = st.radio(
    "Navigation", 
    nav_options, 
    index=nav_options.index(st.session_state.active_tab) if st.session_state.active_tab in nav_options else 0,
    horizontal=True, 
    label_visibility="collapsed",
    key="nav_radio"
)

# Update session state if it drifted (redundant with callback but safe)
st.session_state.active_tab = selection

# ==========================================
# TAB: MY GALLERY
# ==========================================
if selection == "My Gallery":
    with st.container():
        st.markdown("### Personal Gallery")
    
        if not st.session_state.get("authenticated"):
            st.warning("Please login to see your gallery.")
        else:
            username = st.session_state.current_user.get("username")
            user_root = os.path.join("output", "users", username)
            abs_root = os.path.abspath(user_root)
            
            col_gal_head, col_gal_ref = st.columns([3, 1])
            with col_gal_head:
                 if os.getenv("S3_BUCKET_NAME"):
                     st.caption(f"☁️ Cloud Gallery: `s3://{os.getenv('S3_BUCKET_NAME')}/users/{username}`")
                 else:
                     st.caption(f"📂 Gallery Path: `{abs_root}`")
            with col_gal_ref:
                 if st.button("🔄 Refresh"):
                     if "gallery_all_images_meta" in st.session_state:
                         del st.session_state.gallery_all_images_meta
                     
                     # Clear scan key to force re-fetch
                     scan_key = f"gallery_scan_done_{username}"
                     if scan_key in st.session_state:
                         del st.session_state[scan_key]
                         
                     st.rerun()
        
        my_images = []
        
        # --- S3 CLOUD SCAN ---
        if os.getenv("S3_BUCKET_NAME"):
            try:
                import boto3
                bucket = os.getenv("S3_BUCKET_NAME")
                s3 = boto3.client('s3', region_name=os.getenv("AWS_REGION", "ap-southeast-2"))
                prefix = f"users/{username}/"
                
                # PAGINATION LOGIC
                IMAGES_PER_PAGE = 50
                
                # Check scan state to prevent loops
                scan_key = f"gallery_scan_done_{username}"
                
                if "gallery_page" not in st.session_state:
                    st.session_state.gallery_page = 0
                    
                # 1. Fetch Metadata (cached in session state to avoid re-scanning on every interaction)
                # We only re-scan if explicitly refreshed or if cache is missing
                if "gallery_all_images_meta" not in st.session_state or not st.session_state.get(scan_key):
                    all_images_meta = []
                    
                    paginator = s3.get_paginator('list_objects_v2')
                    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
                    
                    for page in pages:
                        for obj in page.get('Contents', []):
                            key = obj['Key']
                            if key.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                                if "/Assets/" not in key:
                                    # Store ONLY metadata, not the signed URL yet
                                    all_images_meta.append({
                                        "key": key,
                                        "name": os.path.basename(key),
                                        "time": obj.get('LastModified').timestamp()
                                    })
                    
                    # Sort Newest First
                    all_images_meta.sort(key=lambda x: x["time"], reverse=True)
                    st.session_state.gallery_all_images_meta = all_images_meta
                    st.session_state[scan_key] = True  # Mark scan as done for this user
                
                # 2. Slice for Current Page
                meta_list = st.session_state.gallery_all_images_meta
                total_images = len(meta_list)
                total_pages = max(1, (total_images + IMAGES_PER_PAGE - 1) // IMAGES_PER_PAGE)
                
                # Ensure page is valid
                current_page = st.session_state.gallery_page
                if current_page >= total_pages:
                    current_page = total_pages - 1
                    st.session_state.gallery_page = current_page
                if current_page < 0:
                    current_page = 0
                    st.session_state.gallery_page = 0
                    
                start_idx = current_page * IMAGES_PER_PAGE
                end_idx = start_idx + IMAGES_PER_PAGE
                page_meta = meta_list[start_idx:end_idx]
                
                # 3. Generate URLs ONLY for current page
                for item in page_meta:
                    url = s3.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': bucket, 'Key': item['key']},
                        ExpiresIn=3600 # 1 hour is enough for view
                    )
                    my_images.append({
                        "src": url,
                        "name": item['name'],
                        "time": item['time']
                    })
                    
                # Pagination Controls
                st.caption(f"Showing {start_idx+1}-{min(end_idx, total_images)} of {total_images} images")
                
                col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
                with col_p1:
                    if st.button("⬅️ Previous", disabled=(current_page == 0)):
                        st.session_state.gallery_page -= 1
                        st.rerun()
                with col_p2:
                    st.markdown(f"<div style='text-align: center'>Page {current_page + 1} of {total_pages}</div>", unsafe_allow_html=True)
                with col_p3:
                    if st.button("Next ➡️", disabled=(current_page >= total_pages - 1)):
                        st.session_state.gallery_page += 1
                        st.rerun()

            except Exception as e:
                st.error(f"Gallery S3 Scan Error: {e}")
                
        # --- LOCAL SCAN (Fallback or Hybrid) ---
        elif os.path.exists(user_root):
            # ... (Local scan logic) ...
            local_imgs = []
            for root, dirs, files in os.walk(user_root):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and "Assets" not in root:
                        full_path = os.path.join(root, file)
                        local_imgs.append({
                            "src": full_path, 
                            "name": file,
                            "time": os.path.getmtime(full_path),
                            "is_local": True
                        })
            local_imgs.sort(key=lambda x: x["time"], reverse=True)
            my_images.extend(local_imgs)

        
        if not my_images:
            st.info(f"No images found for `{username}` yet. Generate something in the Wizard or Series tab!")
        else:
            st.write(f"Found {len(my_images)} images.")
            # Display Grid
            # Display Grid
            cols = st.columns(4)
            for idx, item in enumerate(my_images):
                with cols[idx % 4]:
                    # Functional Gallery Card
                    st.image(item["src"], use_container_width=True)
                    
                    c_view, c_dl = st.columns([1, 1])
                    with c_view:
                        if st.button("🔍", key=f"view_{idx}", help="Zoom Image"):
                            st.session_state[f"zoom_img_{idx}"] = True
                    
                    with c_dl:
                        # Download Logic
                        if os.path.exists(os.path.abspath(item.get("src", ""))):
                             with open(item["src"], "rb") as file:
                                 st.download_button("Download", data=file, file_name=item["name"], key=f"dl_{idx}")
                        else:
                             # S3/URL Link
                             st.link_button("Download", item["src"])

                    # Zoom Modal (Expander hack or Dialog)
                    if st.session_state.get(f"zoom_img_{idx}"):
                        st.markdown(f"**{item['name']}**")
                        st.image(item["src"], use_container_width=True)
                        if st.button("Close View", key=f"close_{idx}"):
                            st.session_state[f"zoom_img_{idx}"] = False
                            st.rerun()

# ==========================================
# TAB: ASSET LIBRARY
# ==========================================
if selection == "Asset Library":
    with st.container():
        username = st.session_state.current_user.get("username")
        user_asset_root = os.path.join("output", "users", username, "Assets")
        
        col_up_1, col_up_2 = st.columns([1, 2])
        
        with col_up_1:
            st.info("How it works:\n\n1. Select a category (e.g. Characters).\n2. Upload an image.\n3. Give it a name.\n4. It's now usable in Wizard & World Builder!")
            
        with col_up_2:
            st.markdown("##### Upload New Asset")
            
            # Category Map
            cat_map = {
                "Characters": "Characters",
                "Outfits": "Outfits",
                "Environments": "Environments",
                "Vibes": "Vibes",
                "Props": "Props",
                "Pets": "Pets",
                "Friends": "Friends",
                "Vehicles": "Vehicles"
            }
            
            target_cat = st.selectbox("Category", list(cat_map.keys()))
            uploaded_files = st.file_uploader("Choose Images", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)
            
            # Optional Name Override (Only applies if single file, or strictly prefixes?)
            # User request: "Original file name should be saved... shouldn't have to rename"
            # So custom_name is truly optional or for prefixing.
            custom_name_prefix = st.text_input("Name Prefix (Optional)", placeholder="Leave empty to use filenames")
            
            if st.button("Save to Library", type="primary"):
                if not uploaded_files:
                    st.error("Please upload files.")
                else:
                    save_dir = os.path.join(user_asset_root, cat_map[target_cat])
                    os.makedirs(save_dir, exist_ok=True)
                    
                    count = 0
                    for up_file in uploaded_files:
                        # 1. Determine Name
                        if custom_name_prefix:
                             # Use prefix + index if multiple? Or just prefix if one?
                             # Let's clean filename
                             f_clean = os.path.splitext(up_file.name)[0]
                             final_name = f"{custom_name_prefix} {f_clean}"
                        else:
                             final_name = os.path.splitext(up_file.name)[0]
                             
                        # Sanitize
                        final_name = "".join([c for c in final_name if c.isalnum() or c in (' ', '-', '_')]).strip()
                        ext = os.path.splitext(up_file.name)[1]
                        
                        # 2. Save File
                        target_path = os.path.join(save_dir, f"{final_name}{ext}")
                        with open(target_path, "wb") as f:
                            f.write(up_file.getbuffer())
                            
                        # 3. SMART INJECT (Instant UI Update)
                        # Add to Session State so it appears in dropdowns immediately
                        # Key format: "(My) Name"
                        mem_key = f"(My) {final_name}"
                        # Map back to internal Keys
                        # cat_map keys are UI keys (Characters), we need internal usage keys (characters)
                        internal_cat_map = {
                            "Characters": "characters", "Outfits": "outfits", "Environments": "locations",
                            "Vibes": "vibes", "Props": "props", "Pets": "pets", "Friends": "relations", "Vehicles": "vehicles"
                        }
                        int_key = internal_cat_map.get(target_cat)
                        
                        if int_key and "global_assets" in st.session_state:
                             st.session_state.global_assets[int_key][mem_key] = target_path
                        
                        # --- S3 SYNC (Restored per-file) ---
                        if os.getenv("S3_BUCKET_NAME"):
                             try:
                                 from execution.s3_uploader import upload_file_obj 
                                 # Key: users/{user}/Assets/{Category}/{Filename}
                                 s3_key = f"users/{username}/Assets/{cat_map[target_cat]}/{final_name}{ext}"
                                 
                                 # Upload
                                 # We can upload the buffer directly or the file
                                 with open(target_path, "rb") as f_up:
                                     upload_file_obj(f_up, object_name=s3_key)
                                     
                                 count += 1
                             except Exception as e:
                                 st.error(f"S3 Upload Error for {final_name}: {e}")
                        else:
                             count += 1
                             
                    st.success(f"Saved {count} assets! Check dropdowns instantly.")
                    # NO RERUN needed because we updated State.
                            
                    st.success(f"Saved **{final_name}** to {target_cat}!")
                    
                    # Update Manifest Logic
                    # We just added a file. We should update the manifest if it exists, or delete it to force a rescan.
                    # Deleting is safer and forces a sync on next load (which will recreate it).
                    # Actually, since load_assets creates it if missing, deleting is a perfect detailed invalidation strategy.
                    
                    user_manifest_path = os.path.join(user_asset_root, "user_manifest.json")
                    if os.path.exists(user_manifest_path):
                        try:
                            # Option A: Delete to force refresh
                            os.remove(user_manifest_path)
                            # Option B: Append to it (Complex, risky if schema changes)
                        except Exception:
                            pass
                    
                    # Clear Cache to allow new asset to show
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    
                    time.sleep(1)
                    st.rerun()

        st.divider()
        st.markdown("#### 📂 Your Library")
        
        # Display directly from Loaded Assets (which includes S3 URLs if in Cloud Mode)
        # We filter for items starting with "(My)" which load_assets.py applies to user content
        
        user_cats = {
            "Characters": "characters",
            "Outfits": "outfits",
            "Environments": "locations", # Mapped
            "Vibes": "vibes",
            "Props": "props", 
            "Pets": "pets",
            "Friends": "relations",
            "Vehicles": "vehicles"
        }
        
        found_any = False
        
        for ui_cat, data_key in user_cats.items():
            # Get all assets for this category
            # all_dict is {Name: Path/URL}
            all_dict = assets.get(data_key, {})
            
            # Filter for User Assets (marked with (My) prefix or checking if it's an S3 URL with 'users/'?)
            # The cleanest way is relying on the keys from load_assets
            my_items = {k: v for k, v in all_dict.items() if "(My)" in k}
            
            if my_items:
                found_any = True
                with st.expander(f"{ui_cat} ({len(my_items)})", expanded=False):
                    c_grid = st.columns(6)
                    for i, (name, url) in enumerate(my_items.items()):
                        # Clean name for display: "(My) Name" -> "Name"
                        clean_name = name.replace("(My) ", "")
                        
                        with c_grid[i % 6]:
                            st.image(url, caption=clean_name, use_container_width=True)
                            
                            # DELETE BUTTON
                            # Use ui_cat to ensure uniqueness across categories (e.g. Vibes vs Locations acting as fallback)
                            if st.button("🗑️", key=f"del_{ui_cat}_{i}_{name}", help=f"Delete {clean_name}"):
                                try:
                                    # 1. Determine Folder Name from Internal Key
                                    # data_key is 'characters', 'outfits', etc.
                                    # We need 'Characters', 'Outfits' for disk/S3
                                    folder_map = {
                                        "characters": "Characters", "outfits": "Outfits", 
                                        "locations": "Environments", "vibes": "Vibes", 
                                        "props": "Props", "pets": "Pets", 
                                        "relations": "Friends", "vehicles": "Vehicles"
                                    }
                                    folder_name = folder_map.get(data_key, data_key.capitalize())
                                    
                                    # Handle URL parameters for S3 Presigned URLs
                                    clean_url = url.split('?')[0]
                                    fname = os.path.basename(clean_url)
                                    
                                    # 2. Local Delete (Construct path explicitly)
                                    # user_asset_root is available in scope
                                    local_path = os.path.join(user_asset_root, folder_name, fname)
                                    if os.path.exists(local_path):
                                        os.remove(local_path)
                                        # Also try to remove json metadata if it exists
                                        meta = local_path.replace(os.path.splitext(local_path)[1], ".json")
                                        if os.path.exists(meta): os.remove(meta)
                                        st.toast(f"Deleted local file: {clean_name}")
                                    elif os.path.exists(url) and url != local_path:
                                        # Fallback if url was actually a different local path
                                        os.remove(url)
                                    
                                    # 3. S3 Delete
                                    if os.getenv("S3_BUCKET_NAME"):
                                        # Construct Key: users/{user}/Assets/{Folder}/{Filename}
                                        s3_key = f"users/{username}/Assets/{folder_name}/{fname}"
                                        delete_file(s3_key)
                                        st.toast(f"Deleted from Cloud: {clean_name}")
                                        
                                    # 4. State Update
                                    if data_key in st.session_state.global_assets:
                                        if name in st.session_state.global_assets[data_key]:
                                            del st.session_state.global_assets[data_key][name]
                                            
                                    # 5. Clear Cache & Rerun
                                    st.cache_data.clear()
                                    time.sleep(0.5)
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"Delete Failed: {e}")
                            
        if not found_any:
            st.info("No custom assets found yet. Upload one above!")
            
        # Debug Info for User Peace of Mind
        if os.getenv("S3_BUCKET_NAME"):
            st.success(f"☁️ Cloud Mode Active: Syncing with S3 ({os.getenv('S3_BUCKET_NAME')})")
        else:
            if os.path.exists(user_asset_root):
                st.caption(f"📂 Local Storage: {user_asset_root}")
            else:
                st.warning("⚠️ Local Storage Missing (Expected on Cloud if S3 not fully synced)")


# ==========================================
# TAB 1: WORKFLOW WIZARD (Existing Logic)
# ==========================================
if selection == "Workflow Wizard":
    with st.container():
        st.markdown("### Step-by-Step Content Creator")
        
        # --- UI Inputs ---
        # --- UI Inputs ---
        # --- UI Inputs (Fragmented for Performance) ---
        @st.fragment
        def wizard_selectors(vibes, outfits, characters, v_data, o_data, c_data):
            c_v, c_o, c_c = st.columns(3)
            with c_v:
                card_begin()
                st.markdown("#### 1. Vibe")
                v = st.selectbox("Choose Aesthetic", vibes, label_visibility="collapsed", key="wiz_vibe")
                if v and v in v_data:
                    st.image(v_data[v], use_container_width=True)
                card_end()
                
            with c_o:
                card_begin()
                st.markdown("#### 2. Outfit")
                o = st.selectbox("Choose Outfit", outfits, label_visibility="collapsed", key="wiz_outfit")
                if o and o in o_data:
                    st.image(o_data[o], use_container_width=True)
                card_end()
    
            with c_c:
                card_begin()
                st.markdown("#### 3. Character")
                c = st.selectbox("Choose Model", characters, label_visibility="collapsed", key="wiz_char")
                if c and c in c_data:
                    st.image(c_data[c], use_container_width=True)
                card_end()
    
        # Call Fragment
        wizard_selectors(vibes_list, outfits_list, characters_list, vibes_data, outfits_data, characters_data)
    
        st.divider()
    
        # V3.9: Wrapped in Form to Prevent Reload Loop
        with st.form(key="wizard_form"):
            # Expandable Camera Controls
            with st.expander("🎥 Camera & Scene Settings", expanded=False):
                col_cam, col_light, col_action = st.columns(3)
                
                with col_cam:
                    st.markdown("**Camera**")
                    sel_camera = st.selectbox("Camera Type", ["Auto"] + knowledge_base.get("cameras", []))
                    sel_lens = st.selectbox("Lens", ["Auto"] + knowledge_base.get("lenses", []))
                    sel_shot = st.selectbox("Shot Type", ["Auto"] + knowledge_base.get("shot_types", []))
                    sel_angle = st.selectbox("Camera Angle", ["Auto"] + knowledge_base.get("camera_angles", []))
                    sel_ar = st.selectbox("Aspect Ratio", ["Auto", "4:5 (Standard)", "16:9 (Cinematic)", "9:16 (Social)"], index=0)
                    sel_style = st.selectbox("Photo Style", ["Auto"] + knowledge_base.get("styles", []))
                    
                with col_light:
                    st.markdown("**Atmosphere**")
                    sel_lighting = st.selectbox("Lighting", ["Auto"] + knowledge_base.get("lighting", []))
                    sel_weather = st.selectbox("Weather", ["Auto"] + knowledge_base.get("weather", []))
                    sel_film = st.selectbox("Film Stock (Grain)", ["Auto"] + knowledge_base.get("film_stocks", []), key="wiz_film_stock")
                    
                with col_action:
                    st.markdown("**Action & Tone**")
                    sel_action = st.selectbox("Subject Action", ["Auto"] + knowledge_base.get("actions", []), key="wiz_action")
                    sel_emotion = st.selectbox("Emotion", ["Auto"] + knowledge_base.get("emotions", []), key="wiz_emotion")
                    sel_filter = st.selectbox("Filter / Look", ["Auto"] + knowledge_base.get("filters", []), key="wiz_filter")
    
            # Custom Direction
            st.subheader("4. Creative Direction")
            custom_scenario = st.text_input("Scenario / Context", placeholder="e.g. At a luxury coffee shop in Paris...")
            custom_notes = st.text_area("Specific Details", placeholder="Enter any extra details here...")
            
            # Advanced Settings & Variants
            col_adv, col_count = st.columns([3, 1])
            
            with col_adv:
                with st.expander("⚙️ Advanced Brain Settings"):
                     st.caption("Brain: Gemini 2.0 Flash (Optimized for Cost)")
                     prompt_engine = "gemini-2.0-flash" 
                     render_engine = "nano" 
                     likeness = 0.5
                     st.sidebar.success("✅ Running in Low-Cost Mode (Flash 2.0)")
                     # selected_checkpoint removed
                     
            with col_count:
                num_images = st.slider("Generate Count", 1, 4, 1, key="wiz_test_count")
    
            # CRITICAL: Store all form values in session state for Director AI button (outside form)
            st.session_state['wiz_sel_camera'] = sel_camera
            st.session_state['wiz_sel_lens'] = sel_lens
            st.session_state['wiz_sel_shot'] = sel_shot
            st.session_state['wiz_sel_angle'] = sel_angle
            st.session_state['wiz_sel_ar'] = sel_ar
            st.session_state['wiz_sel_style'] = sel_style
            st.session_state['wiz_sel_lighting'] = sel_lighting
            st.session_state['wiz_sel_weather'] = sel_weather
            st.session_state['wiz_sel_film'] = sel_film
            st.session_state['wiz_sel_action'] = sel_action
            st.session_state['wiz_sel_emotion'] = sel_emotion
            st.session_state['wiz_sel_filter'] = sel_filter
            st.session_state['wiz_custom_scenario'] = custom_scenario
            st.session_state['wiz_custom_notes'] = custom_notes
    
            # --- CAMPAIGN BUTTON ---
            col_c_btn, col_c_batch = st.columns([3, 1])
            with col_c_batch:
                campaign_batch = st.number_input("Queue Copies", min_value=1, max_value=10, value=1, help="How many variations to queue?")
    
            submit_wiz = st.form_submit_button("Add to Campaign Queue", type="primary")
    
        if submit_wiz:
            # CHECK CREDITS
            user = st.session_state.current_user.get("username")
            if not auth_mgr.deduct_credits(user, 1):
                st.error("❌ Insufficient Credits! Please top up.")
            else:
                # Retrieve values from Session State (set by Fragment)
                s_char = st.session_state.get("wiz_char")
                s_outfit = st.session_state.get("wiz_outfit")
                s_vibe = st.session_state.get("wiz_vibe")

                # Get path for Vision
                char_path = characters_data.get(s_char, s_char)
                outfit_path = outfits_data.get(s_outfit)
                vibe_path = vibes_data.get(s_vibe)
                
                def clean_val(val): return None if val == "Auto" else val
                
                prompt_data = generate_prompt_content(
                    vibe=clean_val(s_vibe), 
                    outfit=s_outfit, 
                    character=char_path,
                    outfit_path=outfit_path,
                    vibe_path=vibe_path,
                    additional_notes=f"{custom_notes} . Context: {custom_scenario} . Emotion: {clean_val(sel_emotion)} . Style: {clean_val(sel_style) or ''}", 
                    camera=clean_val(sel_camera),
                    lens=clean_val(sel_lens),
                    shot_type=clean_val(sel_shot),
                    angle=clean_val(sel_angle),
                    lighting=clean_val(sel_lighting),
                    weather=clean_val(sel_weather),
                    action=clean_val(sel_action),
                    film_stock=clean_val(sel_film),
                    filter_look=clean_val(sel_filter),
                    aspect_ratio=sel_ar.split(" ")[0], 
                    model_engine=prompt_engine 
                )
                
                prompt_data["likeness_strength"] = likeness # Pass to generator
                
                prompt_data["model_type"] = render_engine 
                # prompt_data["checkpoint"] removed
                
                job_name = f"{s_outfit} - {clean_val(s_vibe)}"
                campaign_mgr.add_job(
                    name=job_name,
                    description=f"Engine: {render_engine}",
                    prompt_data=prompt_data,
                    settings={ "batch_count": campaign_batch },
                    output_folder=get_user_out_dir("Campaign"),
                    char_path=char_path,
                    outfit_path=outfit_path,
                    vibe_path=vibe_path
                )
                msg = f"Added '{job_name}'! (Engine: {render_engine}, Batch: {campaign_batch})"
                st.success(msg)

    st.divider()

    # --- TWO STEP GENERATION ---
    col_wiz_btn1, col_wiz_btn2 = st.columns(2)
    
    # Session State for Wizard Prompt
    if "wiz_generated_prompt" not in st.session_state:
        st.session_state.wiz_generated_prompt = None

    with col_wiz_btn1:
        if st.button("✨ Director Vision AI (Generate Prompt)", type="primary", use_container_width=True):
             with st.spinner("Director is writing master prompt..."):
                # Retrieve values from Session State
                s_char = st.session_state.get("wiz_char")
                s_outfit = st.session_state.get("wiz_outfit")
                s_vibe = st.session_state.get("wiz_vibe")
                
                # Get camera/scene settings from session state (stored in form)
                sel_camera = st.session_state.get('wiz_sel_camera', 'Auto')
                sel_lens = st.session_state.get('wiz_sel_lens', 'Auto')
                sel_shot = st.session_state.get('wiz_sel_shot', 'Auto')
                sel_angle = st.session_state.get('wiz_sel_angle', 'Auto')
                sel_ar = st.session_state.get('wiz_sel_ar', 'Auto')
                sel_style = st.session_state.get('wiz_sel_style', 'Auto')
                sel_lighting = st.session_state.get('wiz_sel_lighting', 'Auto')
                sel_weather = st.session_state.get('wiz_sel_weather', 'Auto')
                sel_film = st.session_state.get('wiz_sel_film', 'Auto')
                sel_action = st.session_state.get('wiz_sel_action', 'Auto')
                sel_emotion = st.session_state.get('wiz_sel_emotion', 'Auto')
                sel_filter = st.session_state.get('wiz_sel_filter', 'Auto')
                custom_scenario = st.session_state.get('wiz_custom_scenario', '')
                custom_notes = st.session_state.get('wiz_custom_notes', '')

                # Get path for Vision
                char_path = characters_data.get(s_char, s_char)
                outfit_path = outfits_data.get(s_outfit)
                vibe_path = vibes_data.get(s_vibe)
                
                # Filter "Auto" values (pass None if Auto)
                def clean_val(val): return None if val == "Auto" else val
                
                prompt_data = generate_prompt_content(
                    vibe=s_vibe, 
                    outfit=s_outfit, 
                    character=char_path,
                    outfit_path=outfit_path,
                    vibe_path=vibe_path,
                    additional_notes=f"{custom_notes} . Context: {custom_scenario} . Emotion: {clean_val(sel_emotion)} . Style: {clean_val(sel_style) or ''}", 
                    camera=clean_val(sel_camera),
                    lens=clean_val(sel_lens),
                    shot_type=clean_val(sel_shot),
                    angle=clean_val(sel_angle),
                    lighting=clean_val(sel_lighting),
                    weather=clean_val(sel_weather),
                    action=clean_val(sel_action),
                    emotion=clean_val(sel_emotion), # Added Emotion
                    film_stock=clean_val(sel_film),
                    filter_look=clean_val(sel_filter),
                    aspect_ratio=sel_ar.split(" ")[0], 
                    model_engine=prompt_engine 
                )
                
                st.session_state.wiz_generated_prompt = prompt_data
                st.toast("Prompt Generated! Review below.")

    # Show Editable Prompt if generated
    if st.session_state.wiz_generated_prompt:
        st.markdown("##### 📝 Review & Edit Prompt")
        
        # We bind this to a separate key to allow editing
        # If the generated prompt changes or is new, we might want to reset? 
        # For simple flow, we default value to what's in session state
        
        wiz_prompt_text = st.text_area(
            "Master Prompt", 
            value=st.session_state.wiz_generated_prompt.get("positive_prompt", ""),
            height=200,
            key="wiz_manual_edit"
        )
        
        with col_wiz_btn2:
             c_q, c_g = st.columns([1, 2])
             with c_q:
                 add_queue = st.button("Add to Queue", use_container_width=True, key="wiz_add_q")
             with c_g:
                 run_now = st.button("🎨 Generate Images", type="primary", use_container_width=True, key="wiz_run")
             
             if add_queue:
                 # Update prompt data
                 final_prompt_data = st.session_state.wiz_generated_prompt.copy()
                 final_prompt_data["positive_prompt"] = wiz_prompt_text
                 final_prompt_data["likeness_strength"] = likeness
                 final_prompt_data["model_type"] = render_engine 
                 
                 # Re-resolve paths
                 s_char = st.session_state.get("wiz_char")
                 s_outfit = st.session_state.get("wiz_outfit")
                 s_vibe = st.session_state.get("wiz_vibe")
                 char_path = characters_data.get(s_char, s_char)
                 outfit_path = outfits_data.get(s_outfit)
                 vibe_path = vibes_data.get(s_vibe)
                 
                 campaign_mgr.add_job(
                    name=f"Wiz_{s_char}_{int(time.time())}",
                    description=f"Wizard: {s_char} in {s_outfit}",
                    prompt_data=final_prompt_data,
                    settings={"batch_count": num_images},
                    output_folder=get_user_out_dir("Wizard"),
                    char_path=char_path,
                    outfit_path=outfit_path,
                    vibe_path=vibe_path
                 )
                 st.success("✅ Added to Campaign Queue!")

             if run_now:
                 with st.status(f"Running workflow ({prompt_engine} + {render_engine})...", expanded=True) as status:
                    st.write(f"Generating {num_images} Image(s)...")
                    
                    # Update prompt data with edited text
                    # We need a deep copy or just modify the dict
                    final_prompt_data = st.session_state.wiz_generated_prompt.copy()
                    final_prompt_data["positive_prompt"] = wiz_prompt_text
                    final_prompt_data["likeness_strength"] = likeness
                    final_prompt_data["model_type"] = render_engine 
                    
                    # Re-resolve paths for execution
                    # Re-resolve paths for execution
                    s_char = st.session_state.get("wiz_char")
                    s_outfit = st.session_state.get("wiz_outfit")
                    s_vibe = st.session_state.get("wiz_vibe")

                    char_path = characters_data.get(s_char, s_char)
                    outfit_path = outfits_data.get(s_outfit)
                    vibe_path = vibes_data.get(s_vibe)
                    
                    # OUTPUT SETUP - User Isolated
                    wiz_out_dir = get_user_out_dir("Wizard")
                    
                    st.write(f"DEBUG: Saving to {os.path.abspath(wiz_out_dir)}")

                    # Parallel Execution
                    from concurrent.futures import ThreadPoolExecutor
                    results = []
                    
                    with ThreadPoolExecutor() as executor:
                        # CRITICAL: Pass the image paths so Generation Logic can see them
                        futures = [executor.submit(generate_image_from_prompt, final_prompt_data, wiz_out_dir, char_path, outfit_path, vibe_path) for i in range(num_images)]
                        for future in futures:
                            results.append(future.result())
                    
                    # Display Results
                    # Create a container for results
                    st.divider()
                    st.markdown("#### 📸 Results")
                    cols = st.columns(num_images)
                    for i, result in enumerate(results):
                        with cols[i]:
                            if result and result.get("status") == "success":
                                img_path = result["image_path"]
                                st.image(img_path, caption=f"Variant {i+1}", use_container_width=True)
                                
                                # Show explicit path
                                abs_path = os.path.abspath(img_path)
                                st.success(f"Saved: {os.path.basename(img_path)}")
                                st.caption(f"📁 {abs_path}")
                                
                                # Add download button
                                c_d, c_s = st.columns(2)
                                with c_d:
                                    with open(img_path, "rb") as f:
                                        st.download_button("⬇️ Download", f, file_name=os.path.basename(img_path), mime="image/png", key=f"dw_{i}")
                                with c_s:
                                    if st.button("📁 Quick Save", key=f"qs_{i}", help="Saves to 'Wizard' category in Assets"):
                                        if st.session_state.get("authenticated"):
                                            user = st.session_state.current_user.get("username")
                                            # Default name to timestamp/index if not providing a form
                                            a_name = f"Wiz_{int(time.time())}_{i}"
                                            res = promote_image_to_asset(img_path, user, "Vibes", a_name, wiz_prompt_text)
                                            if res["status"] == "success":
                                                st.toast(f"Saved to Vibes!")
                                                st.cache_data.clear()
                                            else:
                                                st.error(f"Save Failed: {res.get('error')}")
                            else:
                                st.error("Failed")
                                if result: st.write(result)
                    
                    status.update(label="Workflow Complete!", state="complete", expanded=True)






# ==========================================
# TAB: MINI SERIES STUDIO
# ==========================================
if selection == "Mini Series":
    with st.container():
        from execution.mini_series_ui import mini_series_ui
        mini_series_ui(user_asset_path, outfits_data, vibes_data, assets, knowledge_base, auth_mgr, get_user_out_dir, campaign_mgr)
# ==========================================
# ==========================================
# TAB: ADMIN PANEL
# ==========================================
if selection == "Admin Panel":
    with st.container():
        st.markdown("### 🛡️ School Community Admin")
        st.info("Manage the Allowlist for student access. Only emails in this list can sign up.")

        # Tabs
        tab_list, tab_users, tab_upload, tab_stats = st.tabs(["Active Allowlist", "User Management", "Upload CSV", "System Config"])
        
        with tab_list:
            c_tog, c_add = st.columns([2, 1])
            with c_tog:
                is_enforced = os.getenv("ENFORCE_ALLOWLIST", "True").lower() == "true"
                if st.checkbox("Enforce Allowlist (Reject unknown emails)", value=is_enforced):
                    auth_mgr.toggle_allowlist_enforcement(True)
                    st.toast("Allowlist Enforced")
                else:
                    auth_mgr.toggle_allowlist_enforcement(False)
                    st.warning("Allowlist Disabled: Open Signup Active")
            
            with c_add:
                with st.form("quick_add"):
                    new_email = st.text_input("Quick Add Email")
                    if st.form_submit_button("Add Member"):
                        if "@" in new_email:
                            auth_mgr.add_to_allowlist(new_email.strip())
                            st.success(f"Added {new_email}")
                            st.rerun()
                        else:
                            st.error("Invalid Email")
            
            st.divider()
            rows = auth_mgr.list_allowlist()
            if rows:
                st.dataframe(rows, use_container_width=True, column_config={
                    "0": "Email", "1": "Name", "2": "Active"
                })
            else:
                st.warning("Allowlist is empty.")
        
        with tab_users:
            st.markdown("#### Registered Users")
            all_users = auth_mgr.get_all_users()
            st.dataframe(all_users, use_container_width=True)
            
            st.divider()
            st.markdown("#### User Actions")
            c_u, c_act, c_val = st.columns([2, 2, 2])
            with c_u:
                tgt_user = st.selectbox("Select User", [u['username'] for u in all_users])
            with c_act:
                action = st.selectbox("Action", ["Add Credits", "Reset Password", "Ban User"])
            with c_val:
                val_input = st.text_input("Value (Credits or New Pass)", key="admin_act_val")
                
            if st.button("Execute Action", type="primary"):
                if action == "Add Credits":
                    if val_input.isdigit():
                        auth_mgr.add_credits(tgt_user, int(val_input))
                        st.success(f"Added {val_input} credits to {tgt_user}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Enter a number for credits")
                elif action == "Reset Password":
                    if len(val_input) > 3:
                        auth_mgr.reset_user_password(tgt_user, val_input)
                        st.success(f"Password reset for {tgt_user}")
                    else:
                        st.error("Password too short")
                elif action == "Ban User":
                    if st.checkbox(f"Confirm Delete {tgt_user}?"):
                        if auth_mgr.ban_user(tgt_user):
                            st.success(f"Banned {tgt_user}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Cannot ban admin")

        with tab_upload:
            st.markdown("#### Bulk Add Students")
            uploaded_file = st.file_uploader("Upload CSV (Header: email, name)", type=["csv"])
            if uploaded_file:
                import pandas as pd
                try:
                    df = pd.read_csv(uploaded_file)
                    # Normalize headers
                    df.columns = [c.lower().strip() for c in df.columns]
                    
                    if "email" not in df.columns:
                        st.error("CSV must have an 'email' column.")
                    else:
                        if st.button(f"Import {len(df)} Students"):
                            count = 0
                            for index, row in df.iterrows():
                                email = str(row['email']).strip()
                                name = str(row.get('name', '')).strip()
                                if "@" in email:
                                    if auth_mgr.add_to_allowlist(email, name):
                                        count += 1
                            st.success(f"Successfully added {count} students to Allowlist!")
                except Exception as e:
                    st.error(f"Error parsing CSV: {e}")

        with tab_stats:
            st.write("Coming soon: Usage stats per student.")
if selection == "World Builder":
    with st.container():
        st.markdown("### World Builder")
        st.info("Construct complex scenes with multiple characters, props, and specific assets.")
    
    # Load Real Data
    world_db = load_world_db()
    scenarios = get_scenarios()
    
    # Layout
    # Layout: Full Width for Builder
    # Removed "Asset Database" Column as requested
    
    st.markdown("#### Scenario Director")
    
    # 0. Import Helper
    # Ideally should be at top, but placing here for context
    try:
        from execution.storyboard_utils import generate_storyboard_prompts
    except ImportError as e:
        st.error(f"Failed to import storyboard utils: {e}")
        def generate_storyboard_prompts(s, c, m): return [f"Error: {e}"]

    # 1. Scenario Mode Selection
    with st.container():
        card_begin()
        st.markdown("#### Scenario Director")
        
        # Mode Toggle - CRITICAL: Use key to persist across form submissions
        scenario_mode = st.radio(
            "Scenario Mode",
            ["📚 Pre-built Templates", "✏️ Custom Scenario"],
            horizontal=True,
            key="wb_scenario_mode",  # PERSIST SELECTION
            help="Choose a pre-built scenario template or create your own custom scene"
        )
        
        if scenario_mode == "📚 Pre-built Templates":
            # Existing pre-built scenario logic
            # Sort by Category then Name
            scenario_keys = sorted(
                list(scenarios.keys()),
                key=lambda k: (scenarios[k].get('category', 'Uncategorized'), scenarios[k].get('name', ''))
            )
            
            selected_scenario_key = st.selectbox(
                "Select Scenario Template", 
                scenario_keys, 
                format_func=lambda x: f"[{scenarios[x].get('category', 'General').upper()}] {scenarios[x]['name']}"
            )
            
            if selected_scenario_key:
                scenario = scenarios[selected_scenario_key]
                st.caption(f"💡 Template: {scenario['template_prompt']}")
        else:
            # NEW: Custom Scenario Builder
            st.markdown("##### Create Your Own Scene")
            
            custom_scenario_name = st.text_input(
                "Scenario Name (Optional)", 
                placeholder="e.g., Girls' Night Out, Birthday Celebration, Beach Day..."
            )
            
            custom_scenario_desc = st.text_area(
                "Describe Your Scene",
                placeholder="Describe the scene you want to create. The Director AI will automatically incorporate all your selected assets (characters, outfits, locations, props, etc.) into this scene description.\n\nExample: 'A fun photoshoot at the beach during golden hour' or 'Celebrating a friend's birthday at a rooftop restaurant'",
                height=120,
                help="The Director AI will contextualize all your selected assets into this scenario"
            )
            
            save_as_template = st.checkbox(
                "💾 Save as template for future use",
                help="This will add your custom scenario to the pre-built templates"
            )
            
            
            # Create a mock scenario object for downstream logic
            scenario = {
                "name": custom_scenario_name or "Custom Scene",
                "category": "custom",
                "template_prompt": custom_scenario_desc or "Custom scene with selected assets",
                "is_custom": True  # Flag to trigger Director AI
            }
            selected_scenario_key = "custom_scenario"
            
            # CRITICAL: Store these IMMEDIATELY so form can access them
            st.session_state['wb_current_scenario'] = scenario
            st.session_state['wb_selected_scenario_key'] = selected_scenario_key
            
            # Save as template if requested
            if save_as_template and custom_scenario_name and custom_scenario_desc:
                try:
                    from world_manager import add_asset
                    scenario_key = custom_scenario_name.lower().replace(" ", "_")
                    add_asset("scenarios", scenario_key, {
                        "name": custom_scenario_name,
                        "category": "custom",
                        "template_prompt": custom_scenario_desc
                    })
                    st.success(f"✅ Saved '{custom_scenario_name}' as a template! It will appear in pre-built templates after refresh.")
                except Exception as e:
                    st.error(f"Failed to save template: {e}")
            
            if custom_scenario_desc:
                st.caption(f"✨ Your scene: {custom_scenario_desc[:100]}{'...' if len(custom_scenario_desc) > 100 else ''}")
        
        card_end()
    
    if selected_scenario_key:
        # --- SCENE COMPOSITION UI (Synced with Filesystem) ---
        # Fragment to prevent full reload
        @st.fragment
        def wb_composition_fragment(scenarios, selected_scenario_key):
            assets = st.session_state.global_assets
            temp_selections = {}
            temp_assets = []
            prompt_engine = "gemini-2.0-flash" # Default for World Builder
            
            col_c1, col_c2 = st.columns(2)
            
            with col_c1:
                with st.container():
                    card_begin()
                    st.markdown("##### Cast & Characters")
                    st.markdown("###### 1. Protagonist")
                    
                    
                    characters_data = assets.get('characters', {})
                    wb_char_opts = {**characters_data}
                    wb_char_keys = sorted(list(wb_char_opts.keys()))
                    
                    protag_key = st.selectbox(
                        "Select Protagonist", 
                        wb_char_keys, 
                        format_func=lambda x: wb_char_opts[x].get('name', x) if isinstance(wb_char_opts[x], dict) else x
                    )
                    
                    protag_opts = wb_char_opts  
                    p_final_path = None
                    p_final_name = "Character"
    
                    if protag_key:
                        p_val = protag_opts[protag_key]
                        if isinstance(p_val, dict):
                            p_final_name = p_val['name']
                            p_final_path = p_val.get('default_img')
                        else:
                            # Filesystem Asset
                            filename = protag_key.split('/')[-1]
                            if "default" in filename.lower():
                                 # Use parent dir as name
                                 p_final_name = protag_key.split('/')[-2]
                            else:
                                 p_final_name = os.path.splitext(filename)[0]
                            p_final_path = p_val
                    
                        temp_selections["PROTAGONIST"] = p_final_name
    
                        if p_final_path:
                            siblings = []
                            if os.path.exists(p_final_path):
                                char_dir = os.path.dirname(p_final_path)
                                valid_exts = ('.png', '.jpg', '.jpeg', '.webp')
                                siblings = [f for f in os.listdir(char_dir) if f.lower().endswith(valid_exts) and not f.startswith('.')]
                        
                            if siblings:
                                current_file = os.path.basename(p_final_path)
                                try:
                                    def_idx = siblings.index(current_file)
                                except ValueError:
                                    def_idx = 0
                                
                                selected_var = st.selectbox("Select Specific Look", siblings, index=def_idx, key="protag_var")
                                p_final_path = os.path.join(char_dir, selected_var)
                    
                        if p_final_path:
                            temp_assets.append({"path": p_final_path, "label": "Main Character"})
                            st.image(p_final_path, width=200, caption="Reference LoRA/Image")
    
                    st.caption("Main Character Outfit")
                    fit_opts = assets.get('outfits', {})
                    fit_key = st.selectbox("Select Outfit", ["None"] + list(fit_opts.keys()), key="main_outfit")
                    
                    if fit_key and fit_key != "None":
                        path = fit_opts[fit_key]
                        if isinstance(path, dict): path = path.get('default_img')
                        
                        fit_name = fit_key.split('/')[-1] 
                        if os.path.sep in fit_name: fit_name = os.path.splitext(fit_name)[0]
                        
                        if "default" in fit_name.lower(): fit_name = "Stylish Outfit"
                        
                        temp_selections["OUTFIT"] = fit_name
                        temp_assets.append({"path": path, "label": f"Outfit: {fit_name}"})
                        if path:
                            st.image(path, caption=fit_name)
    
                    st.markdown("###### 2. Friends & Cast")
                    rel_opts = assets.get('relations', {})
                    cast_pool = {**wb_char_opts, **rel_opts}
                    rel_keys = sorted(list(cast_pool.keys()))
                    
                    selected_rels = st.multiselect(
                        "Include People", 
                        rel_keys,
                        format_func=lambda x: cast_pool[x].get('name', x) if isinstance(cast_pool[x], dict) else x
                    )
                
                    rel_names = []
                    if selected_rels:
                        st.caption("Selected Cast:")
                        r_cols = st.columns(len(selected_rels))
                        for idx, k in enumerate(selected_rels):
                            path = cast_pool[k] 
                            name = k 
                            if isinstance(path, dict):
                                 name = path.get('name', k)
                                 path = path.get('default_img', '')
                            else:
                                 clean_name = os.path.splitext(k.split('/')[-1])[0]
                                 if k in wb_char_opts: name = clean_name
                                 else: name = clean_name
                        
                            rel_names.append(name)
                            temp_assets.append({"path": path, "label": f"Cast: {name}"})
                            with r_cols[idx]:
                                if path: st.image(path, caption=name)
    
                    if rel_names:
                        temp_selections["RELATIONS"] = " and ".join(rel_names)
                        st.caption("Selected Cast Outfits:")
                        friend_outfit_details = []
                        f_cols = st.columns(len(selected_rels))
                        for idx, k in enumerate(selected_rels):
                            with f_cols[idx]:
                                 f_name = cast_pool[k]['name'] if isinstance(cast_pool[k], dict) else k.split('/')[-1]
                                 f_fit_opts = assets.get('outfits', {})
                                 if not f_fit_opts: f_fit_opts = {"Casual": "", "Chic": ""}
                                 f_outfit_key = st.selectbox(f"Outfit for {f_name.split()[0]}", list(f_fit_opts.keys()), key=f"fit_{idx}")
                                 f_outfit_path = None
                                 if isinstance(f_fit_opts[f_outfit_key], dict):
                                     f_outfit_name = f_fit_opts[f_outfit_key]['name']
                                     f_outfit_path = f_fit_opts[f_outfit_key].get('default_img')
                                 else:
                                     f_outfit_name = os.path.splitext(f_outfit_key.split('/')[-1])[0]
                                     f_outfit_path = f_fit_opts[f_outfit_key]
                                 temp_assets.append({"path": f_outfit_path, "label": f"Outfit for {f_name}: {f_outfit_name}"}) 
                                 friend_outfit_details.append(f"{f_name} in {f_outfit_name}") 
                                 if f_outfit_path: st.image(f_outfit_path, width=150, caption=f_outfit_name)
                        if friend_outfit_details:
                            temp_selections["FRIEND_OUTFITS"] = ", ".join(friend_outfit_details)
                    else:
                        temp_selections["RELATIONS"] = "nobody"
                    card_end()

            with col_c2:
                with st.container():
                    card_begin()
                    st.markdown("##### Setting & Props")
                    st.markdown("###### 3. Pets")
                    pet_opts = assets.get('pets', {})
                    selected_pets = st.multiselect("Include Pets", list(pet_opts.keys()))
                    pet_names = []
                    if selected_pets:
                        p_cols = st.columns(len(selected_pets))
                        for idx, k in enumerate(selected_pets):
                            path = pet_opts[k]
                            name = k.split('/')[-1]
                            pet_names.append(name)
                            temp_assets.append({"path": path, "label": f"Pet: {name}"})
                            with p_cols[idx]:
                                 if path: st.image(path, caption=name)
                    st.divider()
                    st.markdown("###### 4. Props & Vehicles")
                    prop_opts = assets.get('props', {})
                    veh_opts = assets.get('vehicles', {})
                    all_props = {**prop_opts, **veh_opts}
                    selected_props = st.multiselect("Include Items", list(all_props.keys()))
                    prop_names = []
                    if selected_props:
                         pr_cols = st.columns(min(len(selected_props), 4))
                         for idx, k in enumerate(selected_props):
                             path = all_props[k]
                             name = k.split('/')[-1]
                             prop_names.append(name)
                             temp_assets.append({"path": path, "label": f"Prop: {name}"})
                             col_idx = idx % 4
                             with pr_cols[col_idx]:
                                 if path: st.image(path, caption=name)
                    if prop_names:
                        temp_selections["PROPS"] = ", ".join(prop_names)
                        temp_selections["VEHICLE"] = prop_names[0]
                    else:
                        temp_selections["PROPS"] = "props"
                        temp_selections["VEHICLE"] = "vehicle"
                    st.divider()
                    st.markdown("###### 5. Location")
                    loc_opts = get_assets_by_category("locations")
                    loc_key = st.selectbox("Select Location", ["None"] + list(loc_opts.keys()))
                    if loc_key and loc_key != "None":
                          val = loc_opts[loc_key]
                          path = val['default_img'] if isinstance(val, dict) else val
                          loc_name = loc_key.split('/')[-1]
                          if os.path.sep in loc_name: loc_name = os.path.splitext(loc_name)[0]
                          
                          if "default" in loc_name.lower(): loc_name = "Luxury Location"

                          temp_selections["LOCATION"] = loc_name
                          temp_assets.append({"path": path, "label": "Location"})
                          if path: st.image(path, caption=loc_name, width=300)
                    else:
                          temp_selections["LOCATION"] = "generic location"
                    
                    st.divider()
                    st.markdown("###### 6. Vibe / Atmosphere")
                    vibe_opts = ["Luxury", "Cinematic", "Dark", "Bright", "Cozy", "High Energy", "Chill", "Romantic", "Cyberpunk", "Vintage"]
                    sel_vibe = st.selectbox("Select Vibe", vibe_opts, index=0)
                    temp_selections["VIBE"] = sel_vibe

                    card_end()
            
            # Persist to Session State (Critical for Generator outside fragment)
            st.session_state['wb_selections'] = temp_selections
            st.session_state['wb_assets_to_inject'] = temp_assets
            # Store auxiliary lists (props, pets etc) if needed by prompt logic
            st.session_state['wb_rel_names'] = rel_names
            st.session_state['wb_pet_names'] = pet_names
            st.session_state['wb_prop_names'] = prop_names

        # Call the Fragment
        wb_composition_fragment(scenarios, selected_scenario_key)
        
        # Hydrate Local Vars from storage (for downstream legacy logic)
        current_selections = st.session_state.get('wb_selections', {})
        assets_to_inject = st.session_state.get('wb_assets_to_inject', [])
        rel_names = st.session_state.get('wb_rel_names', [])
        pet_names = st.session_state.get('wb_pet_names', [])
        prop_names = st.session_state.get('wb_prop_names', [])
        
        # V3.9: Wrapped in Form to prevent Camera Settings Reload Loop
        with st.form(key="wb_camera_form"):
            # --- CAMERA CONTROLS ---
            with st.expander("Camera & Scene Settings", expanded=False):
                col_cam, col_light, col_action = st.columns(3)
                with col_cam:
                    st.markdown("**Hardware**")
                    sel_camera = st.selectbox("Camera Type", ["Auto"] + knowledge_base.get("cameras", []), key="wb_cam")
                    sel_lens = st.selectbox("Lens", ["Auto"] + knowledge_base.get("lenses", []), key="wb_lens")
                    sel_shot = st.selectbox("Shot Type", ["Auto", "Close Up", "Medium Shot", "Full Body", "Wide Shot", "Extreme Close Up", "Cowboy Shot", "Overhead"], key="wb_shot") 
                    sel_ar = st.selectbox("Aspect Ratio", ["Auto", "4:5", "16:9", "9:16", "1:1", "3:2"], index=0, key="wb_ar")
    
    
                with col_light:
                    st.markdown("**Lighting & Mood**")
                    sel_lighting = st.selectbox("Lighting", ["Auto"] + knowledge_base.get("lighting", []), key="wb_light")
                    sel_weather = st.selectbox("Weather", ["Auto"] + knowledge_base.get("weather", []), key="wb_weath")
                    sel_film_stock = st.selectbox("Film Stock", ["Auto"] + knowledge_base.get("film_stocks", []), key="wb_stock")
    
                with col_action:
                    st.markdown("**Direction**")
                    sel_film = st.selectbox("Style", ["Auto"] + knowledge_base.get("styles", []), key="wb_film")
                    sel_angle = st.selectbox("Angle", ["Auto"] + knowledge_base.get("camera_angles", []), key="wb_ang") # Fixed key to match KB
                    sel_filter_look = st.selectbox("Filter / Look", ["Auto"] + knowledge_base.get("filters", []), key="wb_look")
    
                    # User Provided Emotions (30 List)
                    emotions = [
                        "Auto", "Confident", "Carefree", "Playful", "Relaxed", "Flirty", "Happy", "Calm", "Curious", 
                        "Focused", "Content", "Empowered", "Soft", "Radiant", "Unbothered", "Dreamy", 
                        "Joyful", "Peaceful", "Excited", "Serene", "Bold", "Mischievous", "Warm", 
                        "Self-assured", "Chill", "Lighthearted", "Magnetic", "Present", "Satisfied", 
                        "Quietly happy", "Seductive", "Boss Bitch", "Hysterical", "Zen" # Kept a few custom ones too
                    ]
                    sel_emotion = st.selectbox("Emotion", emotions, key="wb_emo")
                    
                    # User Provided Actions
                    actions = [
                         "Auto",
                         "Adjusting outfit strap", "Adjusting sunglasses", "Applying lip gloss", "Biting lip playfully", 
                         "Celebrating big play courtside", "Celebrating together", "Checking phone notifications", "Clinking drink glasses",
                         "Crossing arms confidently", "Crossing legs slowly", "Dancing subtly", "Fixing hair casually", "Fixing jacket collar",
                         "Flipping hair back", "Group selfie moment", "Holding drink cup", "Holding sunglasses", 
                         "Hyping each other up", "Journaling quietly", "Laughing lightly", "Laughing mid-conversation", "Laughing with friends",
                         "Leaning against wall", "Leaning casually", "Leaning on railing", "Looking around calmly", 
                         "Looking over shoulder", "Pausing mid-step", "Podcast Host (Speaking into Mic)", "Pointing something out", 
                         "Posing effortlessly", "Resting hands on hips", "Scrolling phone casually", 
                         "Sharing inside joke", "Sipping iced coffee", "Sitting close together", "Sitting poolside relaxed", 
                         "Sitting thoughtfully", "Smiling softly", "Stepping into sunlight", "Stretching arms overhead", 
                         "Stretching neck gently", "Taking a deep breath", "Taking mirror selfie", "Talking mid-conversation",
                         "Tilting head slightly", "Walking confidently forward", "Walking side by side", "Walking with friends"
                     ]
                    sel_action = st.selectbox("Action", actions, key="wb_act")
            
            # --- CUSTOM DETAILS ---
            st.markdown("#### Creative Direction")
            custom_details = st.text_area("Specific Details / Custom Context", placeholder="e.g. Holding a red cup, Laughing uniquely, Cyberpunk neon colors...", help="These details will be added to the prompt.")
    
            # --- PROMPT GENERATION LOGIC UPDATE ---
            # CRITICAL: Get scenario from session state (widgets outside form don't persist)
            scenario = st.session_state.get('wb_current_scenario', scenario)
            
            # Check if this is a custom scenario (requires Director AI)
            is_custom_scenario = scenario.get("is_custom", False)
            
            # CRITICAL: Store flag in session state so it persists on button click
            st.session_state['is_custom_scenario'] = is_custom_scenario
            
            # Prepare prompt based on scenario type
            if is_custom_scenario:
                # NEW: Prepare data for custom scenario Director AI (will execute on button click)
                # Store scenario and settings for Director AI button
                st.session_state['custom_scenario_data'] = {
                    'scenario_concept': scenario['template_prompt'],
                    'current_selections': current_selections,
                    'rel_names': rel_names,
                    'pet_names': pet_names,
                    'prop_names': prop_names,
                    'camera_settings': {
                        'shot': sel_shot,
                        'angle': sel_angle,
                        'lighting': sel_lighting,
                        'emotion': sel_emotion,
                        'action': sel_action,
                        'film': sel_film,
                        'filter_look': sel_filter_look
                    },
                    'custom_details': custom_details
                }
                
                # Build a basic template prompt as fallback
                final_prompt = f"{scenario['template_prompt']} featuring {current_selections.get('PROTAGONIST', 'character')}"
                if current_selections.get('LOCATION'):
                    final_prompt += f" at {current_selections.get('LOCATION')}"
                if current_selections.get('OUTFIT'):
                    final_prompt += f" wearing {current_selections.get('OUTFIT')}"
                if custom_details:
                    final_prompt += f", {custom_details}"
                    
                st.info("ℹ️ Click 'Director Vision AI' below to generate a detailed, immersive prompt for your custom scenario")
                
            else:
                # EXISTING: Pre-built template logic
                # Instead of generic replacement, we prepare the context for the AI
                base_template = scenario['template_prompt']
                for k, v in current_selections.items():
                    base_template = base_template.replace(f"[{k}]", v)
                    
                extras = rel_names + pet_names + prop_names
                extras_str = ", ".join(extras) if extras else "background details"
                base_template = base_template.replace("[PROPS_AND_CAST]", extras_str)
                
                # We pass this 'base_template' as the "Scenario Context" to the generator
                custom_scenario = base_template # Renaming for clarity in next step pass
                
                # st.info(f"**Base Context:** {custom_scenario[:100]}...") # Hidden inside form to reduce clutter
                
                final_prompt = custom_scenario # Start with the base scenario
                final_prompt = final_prompt.replace("[RELATION]", current_selections.get("RELATIONS", "friend"))
                final_prompt = final_prompt.replace("[OUTFIT]", current_selections.get("OUTFIT", "casual outfit"))
        
                # Append Custom Details
                if custom_details:
                    final_prompt += f", {custom_details}"
        
                # Append Friend Outfits
                if "FRIEND_OUTFITS" in current_selections:
                     final_prompt += f", {current_selections['FRIEND_OUTFITS']}"
        
                # Append Camera Settings
                cam_details = []
                if sel_camera != "Auto": cam_details.append(f"shot on {sel_camera}")
                if sel_lens != "Auto": cam_details.append(f"{sel_lens} lens")
                if sel_shot != "Auto": cam_details.append(sel_shot) # Restored Logic
                # sel_shot removed in favor of AR + Angle <-- REMOVING THIS COMMENT
                if sel_lighting != "Auto": cam_details.append(f"{sel_lighting} lighting")
                if sel_angle != "Auto": cam_details.append(f"{sel_angle} angle")
                if sel_film != "Auto": cam_details.append(f"{sel_film} style")
                if sel_film_stock != "Auto": cam_details.append(f"Film Stock: {sel_film_stock}")
                if sel_filter_look != "Auto": cam_details.append(f"Look: {sel_filter_look}")
                
                # New Logic
                if sel_emotion != "Auto": cam_details.append(f"Expression: {sel_emotion}")
                if sel_action != "Auto": cam_details.append(f"Action: {sel_action}")
                
                if cam_details:
                    final_prompt += ", " + ", ".join(cam_details)
                    
                # Fallback for Protagonist if replacement failed (e.g. key mismatch)
                if "[PROTAGONIST]" in final_prompt:
                     # Try to find it again or default
                     p_name = current_selections.get("PROTAGONIST", "The Influencer")
                     final_prompt = final_prompt.replace("[PROTAGONIST]", p_name)
    
            # --- DEBUG: INSPECT STATE BEFORE RUNNING AI ---
            # Collapsed by default to avoid confusion
            with st.expander("🛠️ Advanced Debug Info (Inputs)", expanded=False):
                st.write("**Scenario Type:**", "Custom" if is_custom_scenario else "Pre-built Template")
                st.write("**Current Selections:**", current_selections)
                st.write("**Assets (Visual Refs):**", assets_to_inject)
                st.write("**Final Prompt:**", final_prompt)
                st.write("**Session State Keys:**", list(st.session_state.keys()))

            # --- AI DIRECTOR BUTTON ---
            col_ai_btn, col_blank = st.columns([1, 1])
            with col_ai_btn:
                # FORM SUBMIT BUTTON 1
                run_director = st.form_submit_button("Director Vision AI (Generate Prompt)", help="Uses the World-Class Brain to rewrite this into a masterpiece.")
            
            if run_director:
                with st.spinner("Director is rewriting scene..."):
                    
                   # CHECK: Is this a custom scenario? (Use session state flag)
                    use_custom_flow = st.session_state.get('is_custom_scenario', False) and 'custom_scenario_data' in st.session_state
                    
                    # DEBUG OUTPUT
                    st.write(f"🔍 DEBUG: is_custom_scenario in session = {st.session_state.get('is_custom_scenario', 'NOT SET')}")
                    st.write(f"🔍 DEBUG: custom_scenario_data exists = {'custom_scenario_data' in st.session_state}")
                    st.write(f"🔍 DEBUG: use_custom_flow = {use_custom_flow}")
                    
                    if use_custom_flow:
                        # CUSTOM SCENARIO FLOW - Use new detailed Director AI
                        custom_data = st.session_state['custom_scenario_data']
                        
                        # Build comprehensive asset summary
                        assets_summary = f"""Main Character: {custom_data['current_selections'].get('PROTAGONIST', 'character')}
Outfit: {custom_data['current_selections'].get('OUTFIT', 'casual outfit')}
Location: {custom_data['current_selections'].get('LOCATION', 'generic location')}
Cast/Friends: {custom_data['current_selections'].get('RELATIONS', 'nobody')}
Props: {custom_data['current_selections'].get('PROPS', 'none')}
Vibe: {custom_data['current_selections'].get('VIBE', 'neutral')}"""
                        
                        if custom_data['rel_names']:
                            assets_summary += f"\nFriend Outfits: {custom_data['current_selections'].get('FRIEND_OUTFITS', 'casual')}"
                        if custom_data['pet_names']:
                            assets_summary += f"\nPets: {', '.join(custom_data['pet_names'])}"
                        
                        # Build camera settings summary
                        cam_settings = custom_data['camera_settings']
                        camera_summary = []
                        if cam_settings['shot'] != "Auto": camera_summary.append(f"Shot: {cam_settings['shot']}")
                        if cam_settings['angle'] != "Auto": camera_summary.append(f"Angle: {cam_settings['angle']}")
                        if cam_settings['lighting'] != "Auto": camera_summary.append(f"Lighting: {cam_settings['lighting']}")
                        if cam_settings['emotion'] != "Auto": camera_summary.append(f"Emotion: {cam_settings['emotion']}")
                        if cam_settings['action'] != "Auto": camera_summary.append(f"Action: {cam_settings['action']}")
                        if cam_settings['film'] != "Auto": camera_summary.append(f"Style: {cam_settings['film']}")
                        if cam_settings['filter_look'] != "Auto": camera_summary.append(f"Look: {cam_settings['filter_look']}")
                        
                        camera_str = ", ".join(camera_summary) if camera_summary else "natural"
                        
                        # Build Director AI prompt for custom scenario
                        director_prompt = f"""You are a master cinematic prompt writer for photorealistic image generation. Create a rich, immersive, DETAILED scene description.

SCENARIO CONCEPT: {custom_data['scenario_concept']}

CHARACTERS & ASSETS:
{assets_summary}

CAMERA & STYLE: {camera_str}

ADDITIONAL DETAILS: {custom_data['custom_details'] or 'none'}

CRITICAL REQUIREMENTS:
1. Output as a SINGLE flowing paragraph (NO markdown, NO sections, NO code blocks, NO bullet points)
2. Start with "Photorealistic, hyper-detailed, cinematic"
3. Create a VIVID, IMMERSIVE scene - paint the picture with rich visual details
4. Incorporate EVERY asset listed above naturally into the scene
5. Pay special attention to the "ADDITIONAL DETAILS" - these are user-specified and must be included
6. Include specific details about:
   - Character appearances, expressions, and poses
   - Environment atmosphere, lighting quality, and textures
   - Spatial relationships between characters and props
   - Color palette and mood
   - Camera framing and composition
7. Make it feel like a professional film scene - atmospheric, dimensional, alive
8. Length: 4-6 detailed sentences that build a cohesive visual narrative
9. NO explanations, NO justifications - ONLY the direct image prompt

Write an immersive, detailed prompt now:"""
                        
                        try:
                            import google.generativeai as genai
                            model = genai.GenerativeModel("gemini-2.0-flash")
                            response = model.generate_content(director_prompt)
                            generated_prompt = response.text.strip()
                            
                            # Remove any markdown artifacts if present
                            if "```" in generated_prompt:
                                generated_prompt = generated_prompt.replace("```", "").strip()
                            
                            st.session_state['wb_manual_prompt'] = generated_prompt
                            st.success("✨ Custom Scenario Director AI Complete!")
                            time.sleep(1)
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Director AI error: {e}")
                            # Fallback to simple concatenation
                            fallback = f"{custom_data['scenario_concept']}, {assets_summary.replace(chr(10), ', ')}, {camera_str}"
                            if custom_data['custom_details']:
                                fallback += f", {custom_data['custom_details']}"
                            st.session_state['wb_manual_prompt'] = fallback
                            st.warning("Used fallback prompt generation")
                            st.rerun()
                            
                    else:
                        # PRE-BUILT TEMPLATE FLOW - Use existing visual reference Director AI
                        # 1. Identify Main Assets & Extras

                        main_char_path = None
                        main_outfit_path = None
                        vibe_p = None
                        extras_payload = []
                        
                        for asset in assets_to_inject:
                            lbl = asset.get('label', '')
                            path = asset.get('path')
                            
                            if "Main Character" in lbl:
                                 main_char_path = path
                            elif lbl.startswith("Outfit: "): # Exact main outfit label format
                                 main_outfit_path = path
                            elif lbl == "Location":
                                 vibe_p = path
                            else:
                                 # Friends, Friend Outfits, Pets, Props
                                 extras_payload.append(asset)
                        
                        st.toast(f"Director AI Analyzing: {current_selections.get('PROTAGONIST', 'Character')} + {current_selections.get('OUTFIT', 'Outfit')}... [Cam: {sel_camera}, Act: {sel_action}]")
                    
                        prompt_engine = "gemini-2.0-flash" # User requested specifically (Free Tier)
                        # 2. Call Generator with full context
                        # We treat the current draft as 'additional_notes' context
                        enhanced_res = generate_prompt_content(
                            vibe=current_selections.get("VIBE", "luxury"),
                            outfit=current_selections.get("OUTFIT", "fashion"),
                            character=main_char_path, # Pass the PATH
                            outfit_path=main_outfit_path, # Pass the PATH
                            vibe_path=vibe_p, # Pass Location as Image 3 (Vibe Ref)
                            extra_images=extras_payload, # Pass Friends & Extras
                            
                            # Pass Technical Specs Explicitly
                            camera=(sel_camera if sel_camera != "Auto" else None),
                            lens=(sel_lens if sel_lens != "Auto" else None),
                            shot_type=(sel_shot if sel_shot != "Auto" else None),
                            angle=(sel_angle if sel_angle != "Auto" else None),
                            lighting=(sel_lighting if sel_lighting != "Auto" else None),
                            action=(sel_action if sel_action != "Auto" else None),
                            emotion=(sel_emotion if sel_emotion != "Auto" else None),
                            film_stock=(sel_film_stock if sel_film_stock != "Auto" else None),
                            filter_look=(sel_filter_look if sel_filter_look != "Auto" else None),
                            
                            additional_notes=f"CREATIVE BRIEF: The atmosphere is {current_selections.get('VIBE', 'General')}. Overall style: {sel_film}. CREATE A FRESH, HOLLYWOOD-LEVEL SCENE DESCRIPTION from the visual references and cast list. Do not copy template text.",
                            model_engine=prompt_engine # Use currently selected brain (Gemini 2.0)
                        )
                        
                        if enhanced_res and "positive_prompt" in enhanced_res:
                            # final_prompt = enhanced_res["positive_prompt"] <--- REMOVED to prevent conflict with change detector
                            st.session_state['wb_manual_prompt'] = enhanced_res["positive_prompt"]
                            # Draft state remains unchanged, so the box won't auto-revert
                            st.success("🎬 Director Cut Generated! (See Box Below)")
                            time.sleep(1) # Pause to let user see
                            st.rerun()
    
            # --- STATE MANAGEMENT FOR PROMPT BOX ---
            # We need the box to update when:
            # 1. Dropdowns change (Calculated prompt changes)
            # 2. AI Button is clicked (AI rewrites prompt)
            # 3. User types (Manual edit)
            
            # --- STATE MANAGEMENT FOR PROMPT BOX (FIXED) ---
            # We must track the "Draft" state separately to avoid overwriting AI output
            
            if 'last_draft_state' not in st.session_state:
                st.session_state['last_draft_state'] = final_prompt
            
            # 1. Did the Dropdowns change? (Compare current calculated draft vs last known draft)
            if final_prompt != st.session_state['last_draft_state']:
                 # Dropdowns changed -> Reset box to new draft
                 st.session_state['wb_manual_prompt'] = final_prompt
                 st.session_state['last_draft_state'] = final_prompt
            
            # Initialize key if needed
            if 'wb_manual_prompt' not in st.session_state:
                 st.session_state['wb_manual_prompt'] = final_prompt
    
            # Make Prompt Editable
            final_prompt_val = st.text_area("Final Prompt (Editable)", key="wb_manual_prompt", height=200)
            final_prompt = final_prompt_val
            
            st.markdown("<br>", unsafe_allow_html=True)
            wb_queue = st.checkbox("Add to Campaign Queue", key="wb_queue_check")
            # FORM SUBMIT BUTTON (Generate)
            gen_world = st.form_submit_button("Generate Single Scene", type="primary", use_container_width=True)

    # --- ACTION AREA (Outside Form) ---
    st.divider()
    col_act1, col_act2 = st.columns(2)
    
    with col_act1:
        st.markdown("#### 📸 Quick Shot")
        
        # Generation Logic triggered by Form Submit
        if gen_world:
             # Re-resolve main character path from assets just in case
             main_char_path = None
             for a in assets_to_inject:
                 if "Main Character" in a.get('label', ''):
                     main_char_path = a.get('path')
                     break

             # Check Queue Mode
             if st.session_state.get("wb_queue_check"):
                 campaign_mgr.add_job(
                    name=f"WB_Scene_{int(time.time())}",
                    description="World Builder Scene",
                    prompt_data={
                        "positive_prompt": final_prompt,
                        "aspect_ratio": sel_ar,
                        "model_type": "nano",
                        "assets": assets_to_inject
                    },
                    settings={"batch_count": 1},
                    output_folder=get_user_out_dir("World"),
                    char_path=main_char_path
                 )
                 st.success("✅ Added Scene to Campaign Queue!")
                 
             else:
                 can_proceed = True
                 if st.session_state.get("authenticated"):
                     username = st.session_state.current_user.get("username")
                     if not auth_mgr.deduct_credits(username, 1):
                         st.error("❌ Not enough credits!")
                         can_proceed = False
                     else:
                         st.toast("🪙 1 Credit Deducted")
                 
                 if can_proceed:

                     # Magic UI Progress
                     prog_ph = st.empty()
                     # from execution.magic_ui import circular_progress
                     with prog_ph.container():
                          circular_progress()
                          st.caption("Generating...")
                     
                     wb_payload = {
                         "positive_prompt": final_prompt,
                         "aspect_ratio": sel_ar, 
                         "model_type": "nano", 
                         "assets": assets_to_inject
                     }
                     res = generate_image_from_prompt(wb_payload, get_user_out_dir("World"))
                     
                     prog_ph.empty() # Clear Progress
                     
                     with st.expander("Generation Logs", expanded=False):
                         st.code(res.get("logs", "No logs"))
                         
                     if res["status"] == "success":
                         st.session_state['wb_last_img'] = res["image_path"]
                         if st.session_state.get("authenticated"):
                             time.sleep(0.5)
                             st.rerun()
                     else:
                         # Refund Logic
                         username = st.session_state.current_user.get("username")
                         auth_mgr.add_credits(username, 1)
                         st.error(f"Generation Failed: {res.get('logs')}")
                         st.toast("Credit Refunded")

        # Display Result (Persistent)
        if 'wb_last_img' in st.session_state and os.path.exists(st.session_state['wb_last_img']):
            last_img = st.session_state['wb_last_img']
            st.image(last_img, caption="World Build Result", use_container_width=True)
            
            with open(last_img, "rb") as f:
                st.download_button("⬇️ Download Image", f, file_name=os.path.basename(last_img), mime="image/png")
            
            # Save to Assets Button
            st.divider()
            with st.form("wb_save_asset"):
                c_n, c_s = st.columns([2, 1])
                with c_n:
                    asset_name = st.text_input("Name this Asset", placeholder="e.g. My Beach House")
                with c_s:
                    save_asset = st.form_submit_button("📁 Save to Assets", use_container_width=True)
                
                if save_asset:
                    if asset_name and st.session_state.get("authenticated"):
                        user = st.session_state.current_user.get("username")
                        res = promote_image_to_asset(last_img, user, "Locations", asset_name, final_prompt)
                        if res["status"] == "success":
                            st.success(f"Added to Locations!")
                            st.info(res.get("logs", ""))
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Save Failed: {res.get('error')}")
                    else:
                        st.error("Please provide a name.")
    
    with col_act2:
            st.markdown("#### 🎞️ Storyboard Generator")
            if st.button("Draft Storyboard (4 Shots)"):
                with st.spinner("AI Director is writing script..."):
                    # Pass the FULL prompt (with custom details) as context
                    sb_prompts = generate_storyboard_prompts(scenario['name'], final_prompt)
                    st.session_state['sb_prompts'] = sb_prompts
                    if sb_prompts and not isinstance(sb_prompts[0], str) or (len(sb_prompts) > 0 and "Error" not in sb_prompts[0]):
                        st.success("Storyboard Drafted! See below.")
                    else:
                        st.error(f"Generation failed: {sb_prompts}")
            
            if 'sb_prompts' in st.session_state:
                prompts = st.session_state['sb_prompts']
                edited_prompts = []
                
                # --- BATCH CONTROL ---
                c_sb_q, c_sb_run = st.columns([1, 1])
                
                # Re-resolve main char for logic usage
                main_char_path_sb = None
                for a in assets_to_inject:
                     if "Main Character" in a.get('label', ''):
                         main_char_path_sb = a.get('path')
                         break

                with c_sb_q:
                    if st.button("Add All to Queue"):
                         curr_idx = len(campaign_mgr.queue)
                         for i, p in enumerate(prompts):
                             campaign_mgr.add_job(
                                name=f"SB_Shot_{i+1}_{int(time.time())}",
                                description=f"Storyboard Shot {i+1}",
                                prompt_data={
                                    "positive_prompt": p + f", {final_prompt}", 
                                    "aspect_ratio": sel_ar,
                                    "model_type": "nano",
                                    "assets": assets_to_inject
                                },
                                settings={"batch_count": 1},
                                output_folder=get_user_out_dir("Storyboard"),
                                char_path=main_char_path_sb
                             )
                         st.success(f"Added {len(prompts)} shots to Queue!")
                         
                with c_sb_run:
                    if st.button("🎬 Generate All"):
                         for i, p in enumerate(prompts):
                             # Credit Check Loop
                             can_proceed = True
                             if st.session_state.get("authenticated"):
                                 username = st.session_state.current_user.get("username")
                                 if not auth_mgr.deduct_credits(username, 1):
                                     st.error(f"❌ Not enough credits to generate Shot {i+1}!")
                                     can_proceed = False
                                     break # Stop generation
                             
                             if can_proceed:
                                 with st.spinner(f"Generating Shot {i+1}..."):
                                     wb_payload = {
                                         "positive_prompt": p + f", {final_prompt}", # Append full context
                                         "aspect_ratio": sel_ar, 
                                         "model_type": "nano", 
                                         "assets": assets_to_inject
                                     }
                                 res = generate_image_from_prompt(wb_payload, get_user_out_dir("Storyboard"))
                                 if res["status"] == "success":
                                     st.toast(f"Shot {i+1} Generated! (-1 Credit)")
                                     st.session_state[f"sb_img_{i}"] = res["image_path"] # Saved!
                                 else:
                                     st.error(f"Shot {i+1} Failed")
                                     # Refund 
                                     username = st.session_state.current_user.get("username")
                                     auth_mgr.add_credits(username, 1)
                                     st.toast(f"Shot {i+1} Refunded")
                         
                         if st.session_state.get("authenticated"):
                             st.rerun() # Verify update

                for i, p in enumerate(prompts):
                    col_sb_text, col_sb_img = st.columns([2, 1])
                    
                    with col_sb_text:
                        val = st.text_area(f"Shot {i+1}", value=p, height=100, key=f"sb_{i}")
                        edited_prompts.append(val)
                        
                        if st.button(f"Generate Shot {i+1}", key=f"btn_sb_{i}"):
                            # Credit Check
                            can_proceed = True
                            if st.session_state.get("authenticated"):
                                username = st.session_state.current_user.get("username")
                                if not auth_mgr.deduct_credits(username, 1):
                                    st.error("❌ Not enough credits!")
                                    can_proceed = False
                                else:
                                    st.toast("🪙 1 Credit Deducted")
                            
                            if can_proceed:
                                with st.spinner("Rolling camera..."):
                                    wb_payload = {
                                         "positive_prompt": val, # Use edited text
                                         "aspect_ratio": sel_ar, 
                                         "model_type": "nano", 
                                         "assets": assets_to_inject
                                     }
                                    res = generate_image_from_prompt(wb_payload, get_user_out_dir("Storyboard"))
                                    with st.expander(f"Logs Shot {i+1}", expanded=False):
                                         st.code(res.get("logs", "No logs"))
                                         
                                    if res["status"] == "success":
                                        st.session_state[f"sb_img_{i}"] = res["image_path"]
                                        if st.session_state.get("authenticated"):
                                            time.sleep(1)
                                            st.rerun()
                                    else:
                                        st.error(res["logs"])
                    
                    with col_sb_img:
                        if f"sb_img_{i}" in st.session_state:
                             img_path = st.session_state[f"sb_img_{i}"]
                             st.image(img_path, use_container_width=True)
                             if os.path.exists(img_path):
                                 with open(img_path, "rb") as f:
                                     st.download_button(
                                         "⬇️ Save", 
                                         f, 
                                         file_name=os.path.basename(img_path),
                                         mime="image/png",
                                         key=f"dl_sb_{i}"
                                     )
                
                st.divider()
                if st.button("Add Storyboard to Campaign Queue", type="primary"):
                    # Capture current assets state
                    import copy
                    current_assets = copy.deepcopy(assets_to_inject)
                    
                    count = 0
                    for i, p in enumerate(edited_prompts):
                        # Construct Prompt Data (New Schema)
                        p_data = {
                            "positive_prompt": p + f", {final_prompt}",
                            "aspect_ratio": sel_ar,
                            "model_type": "nano",
                            "assets": current_assets
                        }
                        
                        campaign_mgr.add_job(
                            name=f"Storyboard Shot {i+1}",
                            description=f"Scene: {scenario.get('name', 'Custom')}",
                            prompt_data=p_data,
                            settings={"batch_count": 1},
                            output_folder=get_user_out_dir("Campaign")
                        )
                        count += 1
                    
                    st.success(f"Added {count} shots to Campaign Queue! Go to 'Campaign Queue' tab to run them.")

            # Check prompt preview
            final_prompt = scenario['template_prompt']
            
            # Generic Replacement Logic
            # 1. Known slots
            for k, v in current_selections.items():
                final_prompt = final_prompt.replace(f"[{k}]", v)
            
            # 2. Catch-all: [PROPS_AND_CAST]
            # FIX: Added pets to extras
            extras = rel_names + pet_names + prop_names
            extras_str = ", ".join(extras) if extras else "background details"
            final_prompt = final_prompt.replace("[PROPS_AND_CAST]", extras_str)

            # 3. Clean up generic legacy slots if they exist in template but weren't filled
            final_prompt = final_prompt.replace("[RELATION]", current_selections.get("RELATIONS", "friend"))
            final_prompt = final_prompt.replace("[OUTFIT]", current_selections.get("OUTFIT", "casual outfit")) # Use selected output or fallback

            st.info(f"**Prompt Preview:**\n{final_prompt}")
            
            # 3. Generate Actions
            if st.button("Generate World Scene", type="primary"):
                 prog_ph = st.empty()
                 # from execution.magic_ui import circular_progress
                 with prog_ph.container():
                      circular_progress()
                      st.caption("Generating with Nano...")

                 # Construct Payload
                 wb_payload = {
                     "positive_prompt": final_prompt,
                     "aspect_ratio": "4:5", # Default for social
                     "model_type": "nano", # Force Nano for multi-ref
                     "assets": assets_to_inject # New Field
                 }
                 
                 res = generate_image_from_prompt(wb_payload, get_user_out_dir("World"))
                 prog_ph.empty()
                 
                 if res["status"] == "success":
                     st.image(res["image_path"], caption="World Build Result")
                 else:
                     st.error(f"Failed: {res.get('logs')}")


# ==========================================
# ==========================================
if selection == "Campaign Queue":
    with st.container():
        st.markdown("### Campaign Manager")
        
        # Sync with Backend
        st.session_state.campaign_queue = campaign_mgr.queue
        
        pending_count = len([x for x in st.session_state.campaign_queue if x['status'] == 'pending'])
        
        st.metric("Pending Jobs", pending_count)
    
        # 2. Controls - Auto-Advancing with Stop Capability
        if "campaign_running" not in st.session_state:
            st.session_state.campaign_running = False
    
        col_run, col_stop, col_clear = st.columns([1, 1, 4])
        
        with col_run:
            # Run Button
            if st.button("RUN", type="primary", disabled=st.session_state.campaign_running or pending_count == 0):
                st.session_state.campaign_running = True
                st.rerun()
    
        with col_stop:
            # Stop Button
            if st.button("STOP", disabled=not st.session_state.campaign_running):
                st.session_state.campaign_running = False
                st.warning("Stopping after current task...")
                st.rerun()
                
        with col_clear:
            if st.button("Clear All"):
                campaign_mgr.clear_queue()
                st.rerun()
    
        # --- PROCESSOR LOGIC ---
        if st.session_state.campaign_running:
            status_box = st.empty()
            
            # Check for next job
            job = campaign_mgr.get_next_pending_job()
            
            if job:
                status_box.info(f"Processing: {job['name']}...")
                
                # Execute (Blocking for 1 job)
                try:
                    campaign_mgr.process_job(job)
                    st.toast(f"Finished: {job['name']}")
                    st.rerun() # Loop for next
                except Exception as e:
                    st.error(f"Job Failed: {e}")
                    st.session_state.campaign_running = False
            else:
                status_box.success("All Jobs Completed.")
                st.session_state.campaign_running = False
    
        # 3. Queue Visualization (With Delete)
        st.markdown("#### Job List")
        for i, job in enumerate(st.session_state.campaign_queue):
            col_q_info, col_q_del = st.columns([6, 1])
            
            with col_q_info:
                with st.expander(f"{'DONE' if job['status']=='completed' else 'WAITING'} {job.get('id', 'Unknown')} ({job['status']})"):
                    prompt_text = job.get('data', {}).get('prompt_data', {}).get('positive_prompt', 'No Prompt')
                    st.write(f"**Prompt:** {prompt_text}")
                    st.write(f"**Created:** {job.get('created_at', 'Unknown')}")
                    if job['status'] == 'completed':
                         st.write("**Results:**")
                         # Display Logic?
            
            with col_q_del:
                # Only allow deleting pending or completed tasks, not running ones (to match index)
                if st.button("DEL", key=f"del_job_{i}", help="Delete this task"):
                    campaign_mgr.remove_job(i)
                    st.rerun()

# ==========================================
# ==========================================
# TAB: VIDEO STUDIO
# ==========================================
if selection == "Video Studio":
    with st.container():
        st.markdown("### AI Video Generator (Kling 2.6 / Veo 2.0)")
        st.info("Transform your generated images into high-motion video clips using the latest 2026 models.")
    
    # Sub-tabs for Creation vs Gallery
    v_tab_create, v_tab_gallery = st.tabs(["Generate Video", "Video Gallery (Recover)"])
    
    with v_tab_gallery:
        # Use User Isolated Directory
        vid_dir = get_user_out_dir("Videos")
        
        st.markdown(f"#### Generated Videos (Folder: `{os.path.basename(vid_dir)}`)")
        
        if not os.path.exists(vid_dir):
             st.warning(f"No video folder found at {vid_dir}")
        else:
             # Find MP4s
             videos = [f for f in os.listdir(vid_dir) if f.endswith(".mp4")]
             videos.sort(key=lambda x: os.path.getmtime(os.path.join(vid_dir, x)), reverse=True)
             
             if not videos:
                 st.info("No videos found yet.")
             else:
                 for vid in videos:
                     vid_path = os.path.join(vid_dir, vid)
                     
                     with st.expander(f"- {vid}", expanded=True):
                         c1, c2 = st.columns([3, 1])
                         with c1:
                             st.video(vid_path)
                         with c2:
                             st.markdown("**Actions**")
                             with open(vid_path, "rb") as vf:
                                 st.download_button(
                                     f"Download MP4",
                                     data=vf,
                                     file_name=vid,
                                     mime="video/mp4",
                                     key=f"dl_{vid}"
                                 )
                             st.caption(f"Size: {os.path.getsize(vid_path)/1024/1024:.1f}MB")

    with v_tab_create:
        with st.form(key="video_form"):
            # Model Selection
            st.markdown("**Select Video Engine**")
            video_model = st.selectbox("Engine", ["Kling AI 2.6 (Professional)", "HuMo AI (Human Motion Premium)"], key="vid_model_select")
            
            col_v_in, col_v_set = st.columns([1, 1])
        
            with col_v_in:
                st.markdown("**1. Select Input Image**")
                # Allow uploading OR selecting from recent outputs (mockup for now)
                video_source_img = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="vid_in_img")
                
                if video_source_img:
                    st.image(video_source_img, caption="Input Preview", use_container_width=True)
                
                st.markdown("**2. Motion Settings**")
                col_mv, col_phy = st.columns(2)
                with col_mv:
                    vid_movement = st.selectbox("Camera Move", ["Auto", "Pan Left", "Pan Right", "Zoom In", "Zoom Out", "Handheld", "Drone Orbit"], key="vid_move")
                with col_phy:
                    vid_physics = st.selectbox("Physics Focus", ["Standard", "High Physics", "Jiggle Physics", "Water/Liquids"], help="Enforce specific physics simulations.")
                    
                motion_prompt = st.text_area("Motion Prompt", height=100, placeholder="Describe the movement...", key="vid_prompt_text")
                
                # NOTE: Auto-Generate Vision AI button inside Form acts as Submit. 
                # This is tricky. We'll disable it or move it out if problematic.
                # Actually, submit buttons can distinguish themselves.
                auto_vis = st.form_submit_button("Auto-Generate with Vision AI")
                
                if auto_vis:
                     # ... (Vision logic)
                     # Since this is a submit, it will rerun. We need to handle logic conditionally.
                     # However, generating video is also a submit.
                     # We can't have both run.
                     pass # We will handle logic below outside form? No, inside form but check bools.

            # Settings Column (Dynamic)
            with col_v_set:
                if "Kling" in video_model:
                    st.info("⚡ Engine: **Kling AI 2.6** (Professional)")
                    
                    col_dur, col_qual = st.columns(2)
                    with col_dur:
                        duration = st.selectbox("Duration", ["5s", "10s"])
                    with col_qual:
                        quality = st.selectbox("Quality Mode", ["Professional (High Quality, Slower)", "Standard (Fast, Efficient)"])
                        
                    # Advanced Model Override
                    with st.expander("Advanced Model Settings (Override)", expanded=False):
                         model_version_input = st.text_input("Kling Model Version", value="2.6", help="Code auto-converts '2.6' to 'kling-v2-6'.")
                         st.caption("Available: `2.6` (Latest), `1.6` (Stable), `1.5`.")
                         
                         st.divider()
                         st.markdown("**Cinematic Overrides (Prompt Injection)**")
                         v_stock = st.selectbox("Film Stock", ["None"] + knowledge_base.get("film_stocks", []), key="vid_stock")
                         v_filter = st.selectbox("Filter / Look", ["None"] + knowledge_base.get("filters", []), key="vid_filter")
                         v_movie_style = st.selectbox("Movie Reference", ["None"] + knowledge_base.get("movie_styles", []), key="vid_style")
                         
                         st.markdown("**Action & Transition**")
                         c_act, c_trans = st.columns(2)
                         with c_act:
                             # Actions relevant for video
                             vid_actions = ["None", "Slow Motion Walk", "Turning Head", "Running", "Dancing", "Talking", "Laughing", "Fighting", "Driving", "Flying", "Explosion", "Wind blowing hair"]
                             v_action = st.selectbox("Subject Action", vid_actions, key="vid_action_override")
                         with c_trans:
                             v_trans = st.selectbox("Transition In", ["None"] + knowledge_base.get("transitions", []), key="vid_trans")
    
                    mode_val = "pro" if "Professional" in quality else "std"
                    
                    # Camera Controls
                    camera_data = None
                    with st.expander("Camera & Motion Control", expanded=False):
                         enable_camera = st.checkbox("Enable Camera Control", value=False)
                         if enable_camera:
                             st.caption("Values range from -10 to 10.")
                             c1, c2 = st.columns(2)
                             with c1:
                                  h_val = st.slider("Horizontal (X)", -10.0, 10.0, 0.0, step=0.5, help="Neg: Left, Pos: Right")
                                  v_val = st.slider("Vertical (Y)", -10.0, 10.0, 0.0, step=0.5, help="Neg: Down, Pos: Up")
                                  z_val = st.slider("Zoom", -10.0, 10.0, 0.0, step=0.5, help="Neg: In, Pos: Out")
                             with c2:
                                  pan_val = st.slider("Pan (Rotate V)", -10.0, 10.0, 0.0, step=0.5, help="Neg: Down, Pos: Up")
                                  tilt_val = st.slider("Tilt (Rotate H)", -10.0, 10.0, 0.0, step=0.5, help="Neg: Left, Pos: Right")
                                  roll_val = st.slider("Roll", -10.0, 10.0, 0.0, step=0.5, help="Neg: CCW, Pos: CW")
                             
                             camera_data = {
                                 "type": "simple",
                                 "config": {
                                     "horizontal": h_val,
                                     "vertical": v_val,
                                     "pan": pan_val,
                                     "tilt": tilt_val,
                                     "roll": roll_val,
                                     "zoom": z_val
                                 }
                             }
    
                    # Motion Transfer (Video Reference)
                    st.divider()
                    st.markdown("**Video Driven Motion**")
                    
                    m_tab1, m_tab2 = st.tabs(["URL Input", "Upload Video"])
                    
                    ref_video_url = None
                    ref_orientation = "image"
                    
                    with m_tab1:
                        url_input = st.text_input("Reference Video URL (S3/Public)", help="Paste an `http` URL to a video. Overrides Camera Control.")
                        if url_input: ref_video_url = url_input
                        
                    with m_tab2:
                        st.info("⚠️ **Constraint:** Video must be **≤ 30 seconds** and **< 100MB**.")
                        uploaded_vid = st.file_uploader("Upload Reference Video", type=['mp4', 'mov'])
                        if uploaded_vid:
                             # Size Check (100MB)
                             if uploaded_vid.size > 100 * 1024 * 1024:
                                  st.error(f"File too large ({uploaded_vid.size / 1024 / 1024:.1f}MB). Max 100MB.")
                             else:
                                  with st.spinner("Uploading to S3..."):
                                       # Check if already uploaded in session to avoid re-upload
                                       if 'last_uploaded_vid_name' not in st.session_state or st.session_state['last_uploaded_vid_name'] != uploaded_vid.name:
                                            s3_url = upload_file_obj(uploaded_vid, f"user_uploads/{uploaded_vid.name}")
                                            if s3_url:
                                                 st.session_state['last_uploaded_vid_url'] = s3_url
                                                 st.session_state['last_uploaded_vid_name'] = uploaded_vid.name
                                                 st.success("✅ Uploaded!")
                                            else:
                                                 st.error("Upload failed.")
                                       
                                       if 'last_uploaded_vid_url' in st.session_state:
                                            ref_video_url = st.session_state['last_uploaded_vid_url']
                                            st.caption(f"Using: `{ref_video_url}`")
                    
                    if ref_video_url:
                         st.warning("⚠️ Motion Control Mode Active: Camera settings will be ignored.")
                         # Orientation Logic
                         st.markdown("##### 📐 Match Orientation To:")
                         orient_choice = st.radio(
                             "Orientation Source",
                             ["Image (Best for Style, Max 10s)", "Video (Best for Action, Max 30s)"],
                             help="If your video is >10s, you MUST select 'Video'.",
                             label_visibility="collapsed"
                         )
                         ref_orientation = "video" if "Video" in orient_choice else "image"
    
                elif "HuMo" in video_model:
                    st.info("⚡ Engine: **HuMo AI** (Human Motion)")
                    st.warning("Requires REPLICATE_API_TOKEN. High cost per second (~$0.01/s).")
                    
                    st.markdown("**3. Audio Control (Lip Sync)**")
                    humo_audio = st.file_uploader("Upload Audio (Optional)", type=["mp3", "wav"], help="Add audio to sync motion or lips.")
                    
                    st.markdown("**4. Advanced Settings**")
                    h_steps = st.slider("Inference Steps", 10, 100, 50, help="More steps = higher quality (and cost).")
                    h_guidance = st.slider("Text Guidance", 2.0, 15.0, 5.0)
                    h_audio_guidance = st.slider("Audio Guidance", 2.0, 15.0, 5.5)
    
            st.divider()
            
            gen_video_btn = st.form_submit_button("Generate Video", type="primary")

        # LOGIC HANDLERS (Outside Form, triggered by vars)
        if auto_vis:
            if not video_source_img:
                st.error("Upload an image to analyze.")
            elif not os.getenv("GOOGLE_API_KEY"):
                st.error("Missing GOOGLE_API_KEY for Vision Analysis.")
            else:
                prog_ph = st.empty()
                # from execution.magic_ui import circular_progress
                with prog_ph.container():
                     circular_progress()
                     st.caption("Analyzing Context...")
                
                # Save temp
                temp_path = os.path.join("output", "temp_vision_input.png")
                with open(temp_path, "wb") as f:
                    f.write(video_source_img.getbuffer())
                    
                suggestion = generate_motion_prompt(temp_path, movement_type=vid_movement, physics_focus=vid_physics)
                st.session_state["motion_suggestion"] = suggestion
                st.rerun()

        if "motion_suggestion" in st.session_state:
             # This part is tricky. 'Apply Suggestion' button cannot be outside form targeting inside form.
             # We just show text.
             st.info(f"💡 Suggestion: {st.session_state['motion_suggestion']}")

        if gen_video_btn:
            user = st.session_state.current_user.get("username")
            if not auth_mgr.deduct_credits(user, 5):
                st.error("❌ Need 5 Credits for Video!")
            elif not video_source_img:
                st.error("Please upload an image first.")
            else:
                with st.status("Generating Video...", expanded=True) as status:
                    # Save uploaded file momentarily
                    temp_path = os.path.join("output", "temp_video_input.png")
                    with open(temp_path, "wb") as f:
                        f.write(video_source_img.getbuffer())
                    
                    # INJECT STYLE PROMPT
                    final_motion_prompt = motion_prompt
                    
                    # Only check these keys if they exist (which they do if Kling selected, but safe to check)
                    v_stock_val = None
                    v_filter_val = None
                    
                    # Hacky access to scoped variables? No, need to use st.session_state or re-read
                    if "vid_stock" in st.session_state and st.session_state["vid_stock"] != "None":
                        final_motion_prompt += f", Shot on {st.session_state['vid_stock']}"
                    if "vid_filter" in st.session_state and st.session_state["vid_filter"] != "None":
                        final_motion_prompt += f", {st.session_state['vid_filter']} look"
                    if "vid_style" in st.session_state and st.session_state["vid_style"] != "None":
                        final_motion_prompt += f", {st.session_state['vid_style']}"
                    if "vid_action_override" in st.session_state and st.session_state["vid_action_override"] != "None":
                        final_motion_prompt += f", Action: {st.session_state['vid_action_override']}"
                    if "vid_trans" in st.session_state and st.session_state["vid_trans"] != "None":
                         # Transitions often work best as camera instructions
                        final_motion_prompt += f", {st.session_state['vid_trans']} transition"
                    
                    st.caption(f"Final Prompt: {final_motion_prompt}")

                    result = None
                    
                    if "Kling" in video_model:
                        if not (os.getenv("KLING_ACCESS_KEY") and os.getenv("KLING_SECRET_KEY")):
                             st.error("Missing KLING_ACCESS_KEY/SECRET.")
                             status.update(label="Failed", state="error")
                        else:
                             st.write(f"Sending to Kling AI 2.6 API ({mode_val.upper()} Mode)...")
                             st.write("Processing... (Standard: ~2-5m, Pro: ~5-10m)")
                             
                             result = generate_video_kling(
                                 temp_path, 
                                 final_motion_prompt, 
                                 duration=5, 
                                 model_version=model_version_input, 
                                 quality_mode=mode_val, 
                                 camera_control=camera_data,
                                 ref_video_path=ref_video_url,
                                 ref_orientation=ref_orientation,
                                 output_folder=get_user_out_dir("Videos")
                             )
                    
                    elif "HuMo" in video_model:
                         if not os.getenv("REPLICATE_API_TOKEN"):
                              st.error("Missing REPLICATE_API_TOKEN.")
                              status.update(label="Failed", state="error")
                         else:
                              st.write("Sending to Replicate (HuMo)...")
                              st.write("Processing on 8x H100 GPU (Est ~1-2 mins)...")

                              # Use local temp path - generate_video_humo will upload it securely via Replicate client
                              humo_img_input = temp_path
                              
                              # Handle Audio
                              humo_audio_input = None
                              if humo_audio:
                                  # Save audio locally
                                  audio_path = os.path.join("output", "temp_audio_input.mp3")
                                  with open(audio_path, "wb") as fa:
                                      fa.write(humo_audio.getbuffer())
                                  humo_audio_input = audio_path
                              
                              result = generate_video_humo(
                                  humo_img_input,
                                  final_motion_prompt,
                                  audio_path=humo_audio_input,
                                  num_inference_steps=h_steps,
                                  guidance_scale=h_guidance,
                                  audio_guidance_scale=h_audio_guidance,
                                  output_folder=get_user_out_dir("Videos")
                              )

                    # Common Result Handling
                    if result:
                        if result["status"] == "success":
                            status.update(label="Complete!", state="complete")
                            
                            if result.get("warning"):
                                 st.warning(result["warning"])
                            else:
                                 st.success(f"Video Generated! (Task ID: {result.get('task_id', 'N/A')})")
                            
                            if result.get('video_path'):
                                 st.success(f"💾 Saved to: {result['video_path']}")
                                 
                            if result.get('video_url'):
                                st.write(f"**Direct Link:** [Click to Open]({result.get('video_url')})")
                                st.video(result.get('video_url'))
                                
                                if result.get('video_path') and os.path.exists(result['video_path']):
                                    with open(result['video_path'], "rb") as v_file:
                                        st.download_button(
                                            label="⬇️ Download MP4",
                                            data=v_file,
                                            file_name=os.path.basename(result['video_path']),
                                            mime="video/mp4"
                                        )
                            else:
                                if "video_path" in result and result["video_path"]:
                                     # Local file existed but no URL?
                                     st.video(result["video_path"])
                                else:
                                     st.warning("Video URL/Path not found.")
                                
                            with st.expander("Process Logs", expanded=False):
                                st.write(result.get("logs", []))
                        else:
                            status.update(label="Failed", state="error")
                            st.error(f"Error: {result.get('error')}")
                            with st.expander("Error Logs", expanded=True):
                                 st.write(result.get("logs", []))

# ==========================================
# TAB 8: CHARACTER STUDIO
# ==========================================
if selection == "Character Studio":
    with st.container():
        st.markdown("### Character Studio")
    st.info("Design your cast with precision. Used consistently across the platform.")

    # Fragment to fix "Tab Jump" bug on generation
    @st.fragment
    def character_studio_fragment():
        from execution.character_studio_ui import render_character_studio
        render_character_studio(characters_data, get_user_out_dir, campaign_mgr)
        
    character_studio_fragment()


# ==========================================
# TAB: MULTI-SHOT GENERATOR
# ==========================================
if selection == "Multi-Shot Generator":
    from execution.multishot_ui import render_multishot_ui
    render_multishot_ui(get_user_out_dir)

