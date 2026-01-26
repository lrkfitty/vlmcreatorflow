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
    from load_assets import load_assets
    from generate_prompt import generate_prompt_content
    from generate_image import generate_image_from_prompt
    from campaign_runner import CampaignManager
    from execution.generate_video import generate_video_kling, generate_video_humo
    from execution.s3_uploader import upload_file_obj
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

st.set_page_config(page_title="CreateFlow | Viral Lense Media", layout="wide", page_icon=None)

# --- AUTHENTICATION GATE MOVED AFTER THEME LOADING ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- THEME INJECTION ---
def apply_custom_theme():
    st.markdown("""
    <style>
        /* Import Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@500;700;800&display=swap');
        
        /* GLOBAL LIGHT THEME */
        .stApp {
            background-color: #FFFFFF !important;
            color: #1E293B !important;
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6, .stMarkdown, p, label {
            color: #0F172A !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        h1 {
            font-family: 'Montserrat', sans-serif !important;
            color: #0F172A !important;
            background: none !important;
            -webkit-text-fill-color: #0F172A !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #F8FAFC !important;
            border-right: 1px solid #E2E8F0;
        }
        
        /* Brand */
        .brand-overline {
            text-align: center;
            font-size: 0.75rem;
            letter-spacing: 0.15em;
            color: #64748B !important;
            font-weight: 600;
            margin-top: 1rem;
            text-transform: uppercase;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            justify-content: center;
            background-color: transparent;
            padding-bottom: 1rem;
            border-bottom: 1px solid #E2E8F0;
        }
        .stTabs [data-baseweb="tab"] {
            color: #64748B;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border: none !important;
            padding-bottom: 0.5rem;
            font-family: 'Montserrat', sans-serif !important;
        }
        .stTabs [aria-selected="true"] {
            color: #0F172A !important;
            border-bottom: 2px solid #0F172A !important;
            background-color: transparent !important;
        }

        /* Buttons */
        div.stButton > button {
            border-radius: 4px !important;
            font-family: 'Inter', sans-serif !important;
            text-transform: uppercase;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
            color: #FFFFFF !important;
            border: none;
        }
        div.stButton > button[kind="primary"]:hover {
            background: #334155 !important;
            transform: translateY(-1px);
        }
        
        div.stButton > button[kind="secondary"] {
             background: #FFFFFF !important;
             border: 1px solid #CBD5E1 !important;
             color: #334155 !important;
        }

        /* Inputs */
        .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div, .stMultiSelect > div > div {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            color: #0F172A !important;
            border-radius: 4px;
        }
        
        /* Dropdowns */
        ul[data-testid="stSelectboxVirtualDropdown"] {
             background-color: #FFFFFF !important;
             border: 1px solid #E2E8F0 !important;
        }
        li[role="option"] {
             color: #0F172A !important;
        }
        li[role="option"]:hover {
             background-color: #F1F5F9 !important;
        }
        
        /* Cards / Containers */
        .hub-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }

        /* Hub Card Titles */
        .hub-card h4, .hub-card h5 {
            margin-top: 0 !important;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #F1F5F9;
            margin-bottom: 1rem;
        }
        
        /* Expander Headers */
        .streamlit-expanderHeader {
            background-color: #F8FAFC !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 4px !important;
            color: #0F172A !important;
            font-family: 'Montserrat', sans-serif;
            text-transform: uppercase;
            font-size: 0.85rem !important;
        }
        .streamlit-expanderHeader svg {
            fill: #0F172A !important;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #0F172A !important;
        }
    </style>
    """, unsafe_allow_html=True)

apply_custom_theme()

# --- NEW AUTHENTICATION UI (MULTI-USER) ---
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
if not st.session_state.authenticated:
    try:
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
        st.markdown("<h1 style='text-align: center; font-size: 4.5rem; margin-top: -10px; margin-bottom: 2rem;'>CreateFlow</h1>", unsafe_allow_html=True)
        
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
    if st.session_state.get("authenticated"):
        u_info = st.session_state.get("current_user", {"username": "Ghost"})
        credits = auth_mgr.get_credits(u_info.get("username"))
        st.write(f"👤 **{u_info.get('username')}** ({u_info.get('role', 'Viewer')})")
        c1, c2 = st.columns([3, 1])
        with c1:
             st.write(f"💳 **Credits:** `{credits}`")
        with c2:
             if st.button("🔄", key="refresh_creds", help="Sync Credits"):
                 st.rerun()

        if st.button("Logout"):
            cookie_manager.delete("auth_token")
            st.session_state.authenticated = False
            st.rerun()
    st.divider()

# HEADER
st.markdown("<div class='brand-overline'>Viral Lense Media</div>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center'>CreateFlow</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 3rem;'>Enterprise-Grade Content Workflow</p>", unsafe_allow_html=True)

# Load Assets
user_asset_path = None
if st.session_state.get("authenticated"):
    username = st.session_state.current_user.get("username", "guest")
    user_asset_path = os.path.join("output", "users", username, "Assets")
    
    # Debug
    with st.sidebar.expander("🔍 Asset Debug"):
        st.write(f"User: `{username}`")
        st.write(f"Path: `{user_asset_path}`")
        
        if os.path.exists(user_asset_path):
             st.write("✅ Path Exists")
             # Recursive walk to see actual files
             all_files = []
             for root, dirs, files in os.walk(user_asset_path):
                 for name in files:
                     if not name.startswith('.'):
                         rel_path = os.path.relpath(os.path.join(root, name), user_asset_path)
                         all_files.append(rel_path)
             
             if all_files:
                 st.write("Found Files:", all_files)
             else:
                 st.write("⚠️ Directory exists but is empty.")
        else:
             st.write("❌ Path Missing")

try:
    assets = load_assets(user_assets_dir=user_asset_path) # Pass user path
    
    # Debug
    # st.sidebar.write(f"User Assets Found: {len(assets.get('characters', {}))}")
    vibes_data = assets.get('vibes', {})
    outfits_data = assets.get('outfits', {})

    characters_data = assets.get('characters', {})
    
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
tab_wizard, tab_gallery, tab_assets, tab_series, tab_world, tab_campaign, tab_video, tab_char = st.tabs([
    "Workflow Wizard", 
    "My Gallery",
    "Asset Library",
    "🎬 Mini Series",
    "World Builder",
    "Campaign Queue", 
    "Video Studio",
    "👤 Character Studio"
])

# ==========================================
# TAB: MY GALLERY
# ==========================================
with tab_gallery:
    st.markdown("### 🖼️ personal Gallery")
    
    if not st.session_state.get("authenticated"):
        st.warning("Please login to see your gallery.")
    else:
        username = st.session_state.current_user.get("username")
        user_root = os.path.join("output", "users", username)
        abs_root = os.path.abspath(user_root)
        
        col_gal_head, col_gal_ref = st.columns([3, 1])
        with col_gal_head:
             st.caption(f"📂 Gallery Path: `{abs_root}`")
        with col_gal_ref:
             if st.button("🔄 Refresh"):
                 st.rerun()
        
        # Scan for images
        my_images = []
        if os.path.exists(user_root):
            for root, dirs, files in os.walk(user_root):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        my_images.append(os.path.join(root, file))
        
        # Sort by Modified Time (Newest First)
        my_images.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        if not my_images:
            st.info(f"No images found in `{username}`'s folder yet. Go to 'Workflow Wizard' to create something!")
            st.warning(f"Debug: Folder `{abs_root}` exists? {os.path.exists(user_root)}")
        else:
            st.write(f"Found {len(my_images)} images.")
            # Display Grid
            cols = st.columns(4)
            for idx, img_path in enumerate(my_images):
                with cols[idx % 4]:
                    with st.container(border=True):
                        st.image(img_path, use_container_width=True)
                        st.text(os.path.basename(img_path))
                        
                        # Download
                        with open(img_path, "rb") as f:
                            st.download_button("⬇️", f, file_name=os.path.basename(img_path), key=f"gal_dl_{idx}")


# ==========================================
# TAB: MY ASSETS
# ==========================================
with tab_assets:
    st.markdown("### 🎨 Personal Asset Management")
    st.markdown("Upload your own custom content here. It will automatically appear in your generation dropdowns.")
    
    if not st.session_state.get("authenticated"):
        st.warning("Please login to manage assets.")
    else:
        username = st.session_state.current_user.get("username")
        user_asset_root = os.path.join("output", "users", username, "Assets")
        
        col_up_1, col_up_2 = st.columns([1, 2])
        
        with col_up_1:
            st.info("ℹ️ **How it works:**\n\n1. Select a category (e.g. Characters).\n2. Upload an image.\n3. Give it a name.\n4. It's now usable in Wizard & World Builder!")
            
        with col_up_2:
            st.markdown("##### 📤 Upload New Asset")
            
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
            uploaded_file = st.file_uploader("Choose Image", type=["png", "jpg", "jpeg", "webp"])
            custom_name = st.text_input("Asset Name (Optional)", placeholder="e.g. Cyberpunk Jacket")
            
            if st.button("Save to Library", type="primary"):
                if not uploaded_file:
                    st.error("Please upload a file.")
                else:
                    # Determine paths
                    save_dir = os.path.join(user_asset_root, cat_map[target_cat])
                    os.makedirs(save_dir, exist_ok=True)
                    
                    # Filename logic
                    final_name = custom_name.strip() if custom_name.strip() else os.path.splitext(uploaded_file.name)[0]
                    # Sanitize
                    final_name = "".join([c for c in final_name if c.isalnum() or c in (' ', '-', '_')]).strip()
                    ext = os.path.splitext(uploaded_file.name)[1]
                    
                    filename = f"{final_name}{ext}"
                    full_path = os.path.join(save_dir, filename)
                    
                    # Write
                    with open(full_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                        
                    st.success(f"Saved **{final_name}** to {target_cat}!")
                    
                    # Clear Cache to allow new asset to show
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    
                    time.sleep(1)
                    st.rerun()

        st.divider()
        st.markdown("#### 📂 Your Library")
        
        # Show what they have
        if os.path.exists(user_asset_root):
            for cat in cat_map.values():
                cat_path = os.path.join(user_asset_root, cat)
                if os.path.exists(cat_path):
                    # Filter for valid image files recursively
                    valid_exts = ('.png', '.jpg', '.jpeg', '.webp')
                    found_images = []
                    for root, dirs, files in os.walk(cat_path):
                        for f in files:
                            # Skip hidden files
                            if f.startswith("."): continue
                            if f.lower().endswith(valid_exts):
                                found_images.append(os.path.join(root, f))
                    
                    if found_images:
                        with st.expander(f"📁 {cat} ({len(found_images)})", expanded=False):
                            c_grid = st.columns(6)
                            for i, p in enumerate(found_images):
                                f = os.path.basename(p)
                                # If in a subfolder, show subfolder name in caption
                                rel_p = os.path.relpath(p, cat_path)
                                if os.sep in rel_p:
                                    caption = f"{os.path.dirname(rel_p)} / {f}"
                                else:
                                    caption = f
                                
                                with c_grid[i % 6]:
                                    st.image(p, caption=caption, use_container_width=True)


# ==========================================
# TAB 1: WORKFLOW WIZARD (Existing Logic)
# ==========================================
with tab_wizard:
    st.markdown("### Step-by-Step Content Creator")
    
    # --- UI Inputs ---
    # --- UI Inputs ---
    col_vibe, col_outfit, col_char = st.columns(3)
    
    with col_vibe:
        st.markdown('<div class="hub-card">', unsafe_allow_html=True)
        st.markdown("#### 1. Vibe")
        selected_vibe_name = st.selectbox("Choose Aesthetic", vibes_list, label_visibility="collapsed", key="wiz_vibe")
        if selected_vibe_name:
            st.image(vibes_data[selected_vibe_name], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
            
    with col_outfit:
        st.markdown('<div class="hub-card">', unsafe_allow_html=True)
        st.markdown("#### 2. Outfit")
        selected_outfit_name = st.selectbox("Choose Outfit", outfits_list, label_visibility="collapsed", key="wiz_outfit")
        if selected_outfit_name:
            st.image(outfits_data[selected_outfit_name], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_char:
        st.markdown('<div class="hub-card">', unsafe_allow_html=True)
        st.markdown("#### 3. Character")
        selected_character_name = st.selectbox("Choose Model", characters_list, label_visibility="collapsed", key="wiz_char")
        if selected_character_name:
            st.image(characters_data[selected_character_name], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

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
                sel_ar = st.selectbox("Aspect Ratio", ["9:16 (Story/Reel)", "16:9 (Cinematic)", "1:1 (Square)", "4:5 (Instagram Feed)"])
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
                 # selected_checkpoint removed
                 
        with col_count:
            num_images = st.slider("Generate Count", 1, 4, 1, key="wiz_test_count")

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
                # Get path for Vision
                char_path = characters_data.get(selected_character_name, selected_character_name)
                outfit_path = outfits_data.get(selected_outfit_name)
                vibe_path = vibes_data.get(selected_vibe_name)
                
                def clean_val(val): return None if val == "Auto" else val
                
                prompt_data = generate_prompt_content(
                    vibe=clean_val(selected_vibe_name), 
                    outfit=selected_outfit_name, 
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
                
                job_name = f"{selected_outfit_name} - {clean_val(selected_vibe_name)}"
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
                # Get path for Vision
                char_path = characters_data.get(selected_character_name, selected_character_name)
                outfit_path = outfits_data.get(selected_outfit_name)
                vibe_path = vibes_data.get(selected_vibe_name)
                
                # Filter "Auto" values (pass None if Auto)
                def clean_val(val): return None if val == "Auto" else val
                
                prompt_data = generate_prompt_content(
                    vibe=selected_vibe_name, 
                    outfit=selected_outfit_name, 
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
             if st.button("🎨 Generate Images", type="primary", use_container_width=True):
                 with st.status(f"Running workflow ({prompt_engine} + {render_engine})...", expanded=True) as status:
                    st.write(f"Generating {num_images} Image(s)...")
                    
                    # Update prompt data with edited text
                    # We need a deep copy or just modify the dict
                    final_prompt_data = st.session_state.wiz_generated_prompt.copy()
                    final_prompt_data["positive_prompt"] = wiz_prompt_text
                    final_prompt_data["likeness_strength"] = likeness
                    final_prompt_data["model_type"] = render_engine 
                    
                    # Re-resolve paths for execution
                    char_path = characters_data.get(selected_character_name, selected_character_name)
                    outfit_path = outfits_data.get(selected_outfit_name)
                    vibe_path = vibes_data.get(selected_vibe_name)
                    
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
                                with open(img_path, "rb") as f:
                                    st.download_button("⬇️ Download", f, file_name=os.path.basename(img_path), mime="image/png", key=f"dw_{i}")
                            else:
                                st.error("Failed")
                                if result: st.write(result)
                    
                    status.update(label="Workflow Complete!", state="complete", expanded=True)




# ==========================================
# TAB 2: MINI SERIES STUDIO
# ==========================================
with tab_series:
    st.markdown("### 🎬 Mini Series Studio")
    st.info("Create episodic content with consistent cast, wardrobe, and environments.")

    # --- Session State ---
    if "series_storyboard" not in st.session_state:
        st.session_state.series_storyboard = None

    # --- STEP 1: SERIES BIBLE ---
    with st.expander("📖 Step 1: Series Bible", expanded=True):
        col_sb1, col_sb2 = st.columns([1, 1])
        
        with col_sb1:
            series_title = st.text_input("Series Title", placeholder="The Influencer Life")
            
            # IDENTITY (New V2 Fields)
            st.markdown("#### 🆔 Identity & Tone")
            c_gen, c_tone = st.columns(2)
            with c_gen:
                s_genre = st.selectbox("Genre", ["General", "Rom-com", "Drama", "Crime", "Thriller", "Horror", "Slice of Life"])
            with c_tone:
                s_tone = st.selectbox("Tone", ["Neutral", "Luxury", "Gritty", "Dark", "Soft / Romantic", "Comedic"])
            
            s_len = st.radio("Episode Length", ["30 Seconds", "45 Seconds"], horizontal=True)

            # Cast Selection (Characters + Friends)
            st.markdown("#### 🎭 Cast Selection")
            
            # Use Unified Asset Loader (Matches World Builder)
            char_opts = get_assets_by_category("characters", user_asset_path)
            rel_opts = get_assets_by_category("relations", user_asset_path)
            # Merge for selection
            all_cast_opts = {**char_opts, **rel_opts}
            
            # Unified Cast List
            cast_selection = st.multiselect("Select Cast Members", list(all_cast_opts.keys()))
            
            # Wardrobe & Role Mapping (V2)
            cast_wardrobe_map = {}
            cast_role_map = {}
            
            if cast_selection:
                st.caption("Assign Roles & Wardrobe:")
                for member in cast_selection:
                    st.divider()
                    c_img, c_info = st.columns([1, 4])
                    
                    # Resolve Data & Path (Robust Logic)
                    c_data = all_cast_opts.get(member)
                    c_path = None
                    if isinstance(c_data, dict):
                        c_path = c_data.get('default_img')
                    else:
                        c_path = c_data

                    # Show Thumbnail
                    with c_img:
                        if c_path and (os.path.exists(c_path) or c_path.startswith("http")):
                            st.image(c_path, use_container_width=True)
                        else:
                             st.warning("No IMG")

                    with c_info:
                        st.write(f"**{member.split('/')[-1]}**")
                        c1, c2 = st.columns(2)
                        
                        with c1:
                             # Role Select
                             role = st.selectbox(f"Role", ["Main Character", "Love Interest", "Antagonist", "Friend", "Background"], key=f"role_{member}")
                             cast_role_map[member] = role

                        with c2:
                             # Outfit Select
                             outfit_opts = list(outfits_data.keys())
                             sel_fit = st.selectbox(f"Outfit", ["Default"] + outfit_opts, key=f"series_fit_{member}")
                             cast_wardrobe_map[member] = sel_fit
                             
                             # Show Outfit Preview
                             if sel_fit != "Default":
                                 o_path = outfits_data.get(sel_fit)
                                 if isinstance(o_path, dict): o_path = o_path.get('default_img')
                                 if o_path:
                                     st.image(o_path, width=80)
                                         
                # DEBUG: Check State Sync
                with st.expander("🛠️ Debug: Wardrobe Selections (Raw)", expanded=False):
                    st.write(cast_wardrobe_map)

        with col_sb2:
            st.markdown("#### 🌍 Series Environments")
            # Combine Vibes and Locations
            all_locs = list(vibes_data.keys()) + list(assets.get('locations', {}).keys())
            
            st.write("**Primary Location** (Main Action)")
            series_env = st.selectbox("Choose Primary", ["None"] + all_locs)
            
            if series_env and series_env != "None":
                # Preview
                path = vibes_data.get(series_env) or assets.get('locations', {}).get(series_env)
                if path:
                    if isinstance(path, dict): path = path.get('default_img')
                    st.image(path, caption="Primary Environment")
            
            st.write("**Secondary Location** (B-Roll / Cutaways)")
            sec_env = st.selectbox("Choose B-Roll Vibe", ["None"] + all_locs, key="sec_env")
            
            if sec_env and sec_env != "None":
                # Preview Secondary
                path_sec = vibes_data.get(sec_env) or assets.get('locations', {}).get(sec_env)
                if path_sec:
                    if isinstance(path_sec, dict): path_sec = path_sec.get('default_img')
                    st.image(path_sec, caption="Secondary Environment")

    # --- STEP 2: WRITER'S ROOM ---
    st.markdown("---")
    st.markdown("### ✍️ Writer's Room")
    
    c_script, c_action = st.columns([3, 1])
    with c_script:
        with st.form(key="director_form"):
            series_script = st.text_area("Episode Synopsis & Dialogue Intent", height=200, placeholder="Synopsis: She finds out he's been lying, but he doesn't know she knows yet.\n\nIntent:\nALICE: Cold, distant.\nBOB: Trying too hard to be casual.")
            
            # V3: Hollywood Camera Controls
            with st.expander("🎥 Cinematography Settings (Director's Toolkit)", expanded=False):
                c_cam, c_lens, c_light = st.columns(3)
                with c_cam:
                    s_camera = st.selectbox("Camera Body", ["Auto / Director's Choice"] + knowledge_base.get("cameras", []))
                with c_lens:
                    s_lens = st.selectbox("Lens Package", ["Auto / Director's Choice"] + knowledge_base.get("lenses", []))
                with c_light:
                    s_lighting = st.selectbox("Lighting Style", ["Auto / Director's Choice"] + knowledge_base.get("lighting", []))
                
                c_stock, c_look = st.columns(2)
                with c_stock:
                    s_film_stock = st.selectbox("Film Stock", ["Auto"] + knowledge_base.get("film_stocks", []), key="series_stock")
                with c_look:
                    s_filter_look = st.selectbox("Filter / Look", ["Auto"] + knowledge_base.get("filters", []), key="series_filter")

                c_style, c_trans = st.columns(2)
                with c_style:
                     s_movie_style = st.selectbox("Movie Aesthetic", ["Auto"] + knowledge_base.get("movie_styles", []), key="series_style")
                with c_trans:
                     s_transition_style = st.selectbox("Transition Style (B-Roll)", ["Auto"] + knowledge_base.get("transitions", []), key="series_trans")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_director = st.form_submit_button("✨ Director Vision AI", type="primary", use_container_width=True)

    if submit_director:
            if not series_script:
                st.error("Please enter a synopsis.")
            elif not cast_selection:
                st.error("Please select a cast.")
            else:
                with st.spinner("AI Director is breaking down the script..."):
                    # 1. Clean Cast Names for AI & Map for Lookup
                    # RE-LOAD ASSETS TO MIRROR WORLD BUILDER RESOLUTION
                    char_opts = get_assets_by_category("characters", user_asset_path)
                    rel_opts = get_assets_by_category("relations", user_asset_path)
                    all_cast_opts = {**char_opts, **rel_opts}
                    
                    clean_cast_map = {} # {'Shay': '/path/to/real/shay.png'}
                    clean_names_list = []
                    
                    for full_key in cast_selection:
                        # RESOLVE PATH (The World Builder Way)
                        c_data = all_cast_opts.get(full_key)
                        real_path = None
                        if isinstance(c_data, dict):
                            real_path = c_data.get('default_img')
                        else:
                            real_path = c_data
                            
                        # Extract clean NICKNAME
                        base = full_key.split('/')[-1].replace('.png','').replace('.jpg','').strip()
                        clean_name = base.split(' ')[0]
                        
                        # MAP NICKNAME -> RESOLVED PATH (Critical Fix)
                        if real_path:
                            clean_cast_map[clean_name] = real_path
                            clean_names_list.append(clean_name)
                    
                    # Store map in session for lookup during generation
                    st.session_state.cast_lookup_map = clean_cast_map

                    # Clean Roles Map
                    clean_roles_map = {}
                    if cast_role_map:
                        for full_key, role in cast_role_map.items():
                            base = full_key.split('/')[-1].replace('.png','').replace('.jpg','').strip()
                            c_name = base.split(' ')[0]
                            clean_roles_map[c_name] = role

                    # Clean Wardrobe Map (NEW)
                    clean_wardrobe_map = {}
                    director_refs = [] # List of {path, label}
                    
                    if cast_wardrobe_map:
                        for full_key, outfit in cast_wardrobe_map.items():
                            base = full_key.split('/')[-1].replace('.png','').replace('.jpg','').strip()
                            c_name = base.split(' ')[0]
                            clean_wardrobe_map[c_name] = outfit
                            # FIX: Also store the full base name as a key (e.g. "Shay Blonde Bob")
                            # This allows precise lookup if we know the specific asset variation
                            clean_wardrobe_map[base] = outfit 
                            
                            # Resolve Wardrobe Path for Multimodal
                            if outfit != "Default":
                                o_path = outfits_data.get(outfit)
                                if isinstance(o_path, dict): o_path = o_path.get('default_img')
                                if o_path:
                                    director_refs.append({
                                        "path": o_path, 
                                        "label": f"{base}'s Wardrobe: {outfit}"
                                    })
                        
                        # Store Wardrobe Snapshot for Batch Render (After Loop)
                        st.session_state.cast_wardrobe_map_snapshot = clean_wardrobe_map
                    
                    # Also Add Character Faces (Optional but helpful for casting description)
                    # DEBUG: Visualize the Map Keys
                    with st.expander("🛠️ Debug: Wardrobe Snapshot Keys", expanded=False):
                        st.json(clean_wardrobe_map)
                        st.write("Resolved Director Refs:", director_refs)

                    for c_name, c_path in clean_cast_map.items():
                         director_refs.append({
                             "path": c_path,
                             "label": f"Cast Member: {c_name}"
                         })

                    # V2 API Call (Passing CLEAN NAMES & CLEAN ROLES & WARDROBE & IMAGES)
                    sb_data = parse_script_to_scenes(
                        script_text=series_script, 
                        cast_list=clean_names_list, 
                        environment_name=series_env,
                        genre=s_genre,
                        tone=s_tone,
                        roles_map=clean_roles_map,
                        wardrobe_map=clean_wardrobe_map,
                        ref_images=director_refs, # <--- PASSING THE IMAGES
                        secondary_environment=sec_env,
                        # V3 New Params
                        camera=s_camera,
                        lens=s_lens,
                        lighting=s_lighting,
                        film_stock=s_film_stock,
                        filter_look=s_filter_look,
                        movie_style=s_movie_style,
                        transition_style=s_transition_style
                    )
                    
                    if "error" in sb_data:
                        st.error(sb_data['error'])
                    else:
                        st.session_state.series_storyboard = sb_data
                        
                        # --- STATE FLUSH (Critical Fix for "Blank Prompt") ---
                        # We must clear old widget states so the text_areas reload from the new JSON data
                        keys_to_clear = [k for k in st.session_state.keys() if k.startswith(("p_s", "img_s", "m_s", "btn_s"))]
                        for k in keys_to_clear:
                            del st.session_state[k]

                        st.success("Director Vision Generated!")

    # --- STEP 3: DIRECTOR MODE ---
    if st.session_state.series_storyboard:
        st.markdown("---")
        st.markdown("### 🎬 Director Mode & Storyboard")
        
        sb = st.session_state.series_storyboard
        st.caption(f"Episode: {sb.get('title', 'Untitled')}")
        
        # Iterating Scenes
        generated_shots_data = [] 
        
        # Ensure lookup map exists (handle refresh case)
        if "cast_lookup_map" not in st.session_state:
             # Fallback rebuild if missing - MATCHING WORLD BUILDER LOGIC
             char_opts = get_assets_by_category("characters", user_asset_path)
             rel_opts = get_assets_by_category("relations", user_asset_path)
             all_cast_opts = {**char_opts, **rel_opts}
             
             clean_cast_map = {}
             for full_key in cast_selection:
                c_data = all_cast_opts.get(full_key)
                real_path = None
                if isinstance(c_data, dict):
                    real_path = c_data.get('default_img')
                else:
                    real_path = c_data
                
                base = full_key.split('/')[-1].replace('.png','').replace('.jpg','')
                clean_name = base.split(' ')[0]
                
                if real_path:
                    clean_cast_map[clean_name] = real_path
             st.session_state.cast_lookup_map = clean_cast_map
        
        cast_map = st.session_state.cast_lookup_map

        for scene_idx, scene in enumerate(sb.get('scenes', [])):
            with st.container():
                st.markdown(f"#### Scene {scene.get('id')}: {scene.get('location')}")
                
                shots = scene.get('shots', [])
                for shot_idx, shot in enumerate(shots):
                    key_base = f"s{scene_idx}_sh{shot_idx}"
                    
                    # 2. Resolve Character Asset (Robust Lookup)
                    char_list = shot.get('characters', [])
                    # AI might return "Shay" or "Shay (Happy)", try partial match
                    char_ref_name = char_list[0] if char_list else None
                    char_full_key = None
                    
                    if char_ref_name:
                        # Try exact match
                        char_full_key = cast_map.get(char_ref_name)
                        # Try fuzzy match if exact fail
                        if not char_full_key:
                            for c_name, c_key in cast_map.items():
                                if c_name in char_ref_name or char_ref_name in c_name:
                                    char_full_key = c_key
                                    break
                    
                    # Fallback to first selected cast if no match for Shot 1/2
                    if not char_full_key and cast_selection and not (shot_idx+1 in [3,6,9,12]):
                         char_full_key = cast_selection[0]

                    # Path Resolution (Strict Validation)
                    char_path = characters_data.get(char_full_key) or assets.get('relations', {}).get(char_full_key)
                    if isinstance(char_path, dict): char_path = char_path.get('default_img')
                    
                    # Use 'char_full_key' for wardrobe lookup too
                    outfit_name = cast_wardrobe_map.get(char_full_key, "Default")
                    outfit_path = outfits_data.get(outfit_name)
                    if isinstance(outfit_path, dict): outfit_path = outfit_path.get('default_img')
                    col_txt, col_img = st.columns([1.5, 1])
                    
                    with col_txt:
                        st.markdown(f"**Shot {shot_idx+1}**")
                        
                        # V3: Display Cinematic Metadata
                        meta_cols = st.columns(4)
                        meta_cols[0].caption(f"📏 {shot.get('shot_size', 'Auto')}")
                        meta_cols[1].caption(f"🎥 {shot.get('camera_angle', 'Auto')}")
                        meta_cols[2].caption(f"💡 {shot.get('lighting_type', 'Auto')}")
                        meta_cols[3].caption(f"🎨 {shot.get('composition', 'Auto')}")
                        
                        # V3.7: Editable Cast List (Fixes Ghost Characters / Leaking)
                        # allow user to remove "Boyfriend" if Gemini put him in Shot 1
                        all_cast_keys = list(st.session_state.cast_lookup_map.keys())
                        # Normalize defaults to ensure they exist in options
                        current_chars = shot.get('characters', [])
                        valid_defaults = []
                        for c in current_chars:
                            # Try exact or normalized
                            if c in all_cast_keys: valid_defaults.append(c)
                            elif c.replace('_', ' ').split(' ')[0] in all_cast_keys: 
                                valid_defaults.append(c.replace('_', ' ').split(' ')[0])
                                
                        selected_chars = st.multiselect(
                            "Cast in Shot", 
                            options=all_cast_keys,
                            default=valid_defaults,
                            key=f"cast_sel_{key_base}",
                            label_visibility="collapsed",
                            placeholder="Select Cast..."
                        )
                        # UPDATE SHOT DATA so Generator uses this
                        shot['characters'] = selected_chars
                        
                        # V3.8: Time of Day Selector
                        time_opts = ["Morning", "Noon", "Afternoon", "Golden Hour", "Blue Hour", "Night", "Midnight"]
                        # AI might have provided a time, otherwise default to Day
                        ai_time = shot.get('time_of_day', 'Day')
                        
                        # Normalize AI output to title case for matching
                        ai_time_norm = ai_time.title() if ai_time else "Day"
                        # Find closest match or default
                        def_idx = 0
                        for idx, opt in enumerate(time_opts):
                            if opt.lower() in ai_time_norm.lower():
                                def_idx = idx
                                break
                                
                        selected_time = st.selectbox(
                            "Time of Day", 
                            time_opts, 
                            index=def_idx,
                            key=f"time_{key_base}",
                            label_visibility="collapsed"
                        )
                        selected_time = st.selectbox(
                            "Time of Day", 
                            time_opts, 
                            index=def_idx,
                            key=f"time_{key_base}",
                            label_visibility="collapsed"
                        )
                        shot['time_of_day'] = selected_time

                        # V3.9: Transition Selector (Editable)
                        trans_opts = ["None"] + knowledge_base.get("transitions", [])
                        sel_trans = st.selectbox("Transition", trans_opts, key=f"trans_{key_base}", label_visibility="collapsed")
                        shot['transition'] = sel_trans
                        
                        # Editable Prompt
                        shot_prompt = st.text_area("Visual Prompt", value=shot.get('visual_prompt'), height=250, key=f"p_{key_base}", label_visibility="collapsed")
                        st.caption(f"Length: {len(shot_prompt) if shot_prompt else 0} chars (Target: 800+)")
                        
                        # Controls
                        c_gen, c_type = st.columns([1, 1.5])
                        with c_gen:
                            if st.button(f"Generate Shot {shot_idx+1}", key=f"btn_{key_base}"):
                                user = st.session_state.current_user.get("username")
                                if not auth_mgr.deduct_credits(user, 1):
                                    st.error("❌ No Credits!")
                                else:
                                    with st.spinner("Rolling camera..."):
                                        # Resolve Character (Using Lookup Map for Robustness)
                                        char_list = shot.get('characters', [])
                                        # AI might say "Shay", Map has "Shay" -> Path
                                        char_path = None
                                        char_ref = "Unknown"
                                        
                                        # V3.6: Multi-Character Injection Loop
                                        # Logic: Iterate all characters in the shot to support Two-Shots / Ensemble
                                        final_assets_payload = []
                                        resolved_names = []
                                        
                                        # A. Resolve Lead Characters
                                        if char_list:
                                            for raw_name in char_list:
                                                # 1. Resolve Face
                                                # Lookup Strategy: Exact -> 1st Word -> Normalized 1st Word
                                                naive_key = raw_name.split(' ')[0]
                                                c_path = st.session_state.cast_lookup_map.get(naive_key)
                                                
                                                if not c_path:
                                                    if '_' in raw_name:
                                                        norm_key = raw_name.replace('_', ' ').split(' ')[0]
                                                        c_path = st.session_state.cast_lookup_map.get(norm_key)
                                                        if c_path: naive_key = norm_key # Update key for outfit lookup
                                                
                                                if c_path:
                                                    final_assets_payload.append({
                                                        "path": c_path,
                                                        "label": f"Cast: {raw_name}"
                                                    })
                                                    resolved_names.append(raw_name)
                                                    
                                                    # 2. Resolve Outfit (Linked to this Character)
                                                    w_snapshot = st.session_state.get('cast_wardrobe_map_snapshot', {})
                                                    # Robust Strategy: Full Name -> First Name
                                                    o_name_key = w_snapshot.get(raw_name)
                                                    
                                                    if not o_name_key or o_name_key == "Default":
                                                        o_fallback = w_snapshot.get(naive_key, "Default")
                                                        if o_fallback != "Default": o_name_key = o_fallback
                                                        
                                                    if o_name_key and o_name_key != "Default":
                                                        o_data = outfits_data.get(o_name_key)
                                                        if isinstance(o_data, dict): o_data = o_data.get('default_img')
                                                        if o_data:
                                                            final_assets_payload.append({
                                                                "path": o_data,
                                                                "label": f"Outfit for {raw_name}: {o_name_key}"
                                                            })

                                    # B. Fallback (If NO characters found, but NOT B-Roll)
                                    is_broll = (shot_idx + 1) in [3, 6, 9, 12]
                                    if not final_assets_payload and cast_selection and not is_broll:
                                         # Force Protagonist
                                         first_key = cast_selection[0]
                                         c_data = all_cast_opts.get(first_key)
                                         c_path = c_data.get('default_img') if isinstance(c_data, dict) else c_data
                                         c_name = first_key.split('/')[-1]
                                         
                                         if c_path:
                                             final_assets_payload.append({"path": c_path, "label": f"Cast: {c_name}"})
                                             # Try outfit
                                             w_snapshot = st.session_state.get('cast_wardrobe_map_snapshot', {})
                                             # Try simple lookup
                                             o_key = w_snapshot.get(c_name.split(' ')[0], "Default")
                                             if o_key != "Default":
                                                 o_data = outfits_data.get(o_key)
                                                 if isinstance(o_data, dict): o_data = o_data.get('default_img')
                                                 if o_data:
                                                     final_assets_payload.append({"path": o_data, "label": f"Outfit for {c_name}: {o_key}"})

                                    # Environment Resolution
                                    target_env = sec_env if is_broll and sec_env != "None" else series_env
                                    env_path = vibes_data.get(target_env) or assets.get('locations', {}).get(target_env)
                                    if isinstance(env_path, dict): env_path = env_path.get('default_img')
                                    
                                    if env_path:
                                        final_assets_payload.append({
                                            "path": env_path,
                                            "label": f"Location: {target_env}"
                                        })
                                    
                                    # Generate Prompt Data
                                    
                                    # SAFETY CHECK: Ensure prompt is not empty
                                    # V3.8: Inject Time of Day & Transition
                                    time_setting = shot.get('time_of_day', 'Day')
                                    trans_setting = shot.get('transition', 'None')
                                    # Transitions in prompts act as style/camera guides
                                    trans_text = f"Visual Transition Style: {trans_setting}. " if trans_setting and trans_setting != "None" else ""
                                    
                                    final_shot_prompt = f"Time of Day: {time_setting}. {trans_text}{shot_prompt}"
                                    if not final_shot_prompt or len(final_shot_prompt.strip()) < 5:
                                        st.warning("⚠️ Prompt was empty! Using fallback.")
                                        final_shot_prompt = f"Cinematic shot of {char_ref} in {target_env}, high quality, 8k, detailed."
                                    
                                    p_data = {
                                         "positive_prompt": final_shot_prompt,
                                         "negative_prompt": "blurry, low quality, distortion, ugly face",
                                         "aspect_ratio": "16:9",
                                         "model_type": "nano", 
                                         "assets": final_assets_payload  # <--- UPDATED VARIABLE
                                    }
                                    
                                    # DEBUG: Show User what we are sending
                                    with st.expander(f"🛠️ Debug: Shot {shot_idx+1} Payload", expanded=False):
                                        st.write(final_assets_payload)
                                    
                                    res = generate_image_from_prompt(p_data, get_user_out_dir("Series"))
                                    if res["status"] == "success":
                                        st.session_state[f"img_{key_base}"] = res["image_path"]
                                        st.success("Shot Captured!")
                                    else:
                                        err_msg = str(res.get("logs", "Unknown Error"))
                                        if "SAFETY" in err_msg or "Refusal" in err_msg:
                                            st.warning("🚧 **Action Blocked by Safety Filters**")
                                            st.info("💡 **Tip:** Try removing explicit descriptors like 'curves', 'sheer', or 'revealing' from the prompt text area above.")
                                            with st.expander("Show Detailed Error"):
                                                st.error(err_msg)
                                        else:
                                            st.error(f"Generation Failed: {err_msg}")
                        
                        with c_type:
                            motion_type = st.radio("Media", ["Still", "Kling Video", "Sora 2 Video", "Mocap"], key=f"m_{key_base}", horizontal=True, label_visibility="collapsed")
                            mocap_file = None
                            if motion_type == "Mocap":
                                mocap_file = st.file_uploader("Ref", type=['mp4'], key=f"up_{key_base}", label_visibility="collapsed")

                    with col_img:
                        # Display Generated Image or Placeholder
                        if f"img_{key_base}" in st.session_state:
                            img_p = st.session_state[f"img_{key_base}"]
                            st.image(img_p, caption=f"Shot {shot_idx+1} (Ready)", use_container_width=True)
                            
                            # V3.7: Download Button
                            if os.path.exists(img_p):
                                with open(img_p, "rb") as file:
                                    st.download_button(
                                        label="⬇️ Download Shot",
                                        data=file,
                                        file_name=os.path.basename(img_p),
                                        mime="image/png",
                                        key=f"dl_{key_base}"
                                    )
                                st.caption(f"Saved to: {img_p}")
                        else:
                            st.info("No Image Generated")
                    
                    st.divider()

                    # Store for Batch
                    generated_shots_data.append({
                        "scene_id": scene.get('id'),
                        "shot_id": shot_idx + 1,
                        "prompt": shot_prompt,
                        "type": motion_type,
                        "mocap": mocap_file,
                        "characters": shot.get('characters'),
                        "environment": series_env,
                        "transition": shot.get('transition'),
                        "generated_still": st.session_state.get(f"img_{key_base}") 
                    })
                        
    # --- STEP 4: PRODUCTION ---
    st.markdown("---")
    if st.button("🚀 Produce Episode (Batch Render)", type="primary"):
        if not st.session_state.series_storyboard:
            st.error("No storyboard defined.")
        else:
            with st.status("🎬 Production in progress...", expanded=True) as status:
                st.write("Initializing Batch Queue...")
                
                # ESTIMATE COST
                total_shots = len(generated_shots_data)
                user = st.session_state.current_user.get("username")
                
                if not auth_mgr.deduct_credits(user, total_shots):
                    st.error(f"❌ Insufficient Credits for {total_shots} shots!")
                else:
                    # Output Setup
                    ep_title = st.session_state.series_storyboard.get('title', 'Untitled_Ep').replace(" ", "_")
                base_out = os.path.join(get_user_out_dir("Series"), series_title.replace(" ", "_"), ep_title)
                os.makedirs(base_out, exist_ok=True)
                
                for shot_data in generated_shots_data:
                    s_id = shot_data['scene_id']
                    sh_id = shot_data['shot_id']
                    p_text = shot_data['prompt']
                    m_type = shot_data['type']
                    
                    # SAFETY GUARD: Ensure Prompt Exists
                    if not p_text or len(p_text.strip()) < 5:
                         st.warning(f"⚠️ Shot {s_id}-{sh_id} prompt empty! Using fallback.")
                         p_text = f"Cinematic shot of scene {s_id} shot {sh_id}, high quality, 8k"

                    # V3.8: Inject Time of Day & Transition (Batch)
                    t_day = shot_data.get('time_of_day', 'Day')
                    t_trans = shot_data.get('transition', 'None')
                    t_text = f"Visual Transition Style: {t_trans}. " if t_trans and t_trans != "None" else ""
                    
                    p_text = f"Time of Day: {t_day}. {t_text}{p_text}"
                    
                    st.write(f"Processing Scene {s_id} Shot {sh_id} ({m_type})...")
                    
                    # 1. Image Generation (Always needed as base)
                    # Resolve Assets for JSON Injection (Mirroring World Builder)
                    assets_payload = []
                    
                    # Environment Injection (V3 Update)
                    # Define B-Roll status
                    is_broll = sh_id in [3, 6, 9, 12]
                    
                    # Determine env
                    target_env = sec_env if is_broll and sec_env != "None" else series_env
                    if 'location' in shot_data: target_env = shot_data['location'] # Override if specific
                    
                    env_path = vibes_data.get(target_env) or assets.get('locations', {}).get(target_env)
                    if isinstance(env_path, dict): env_path = env_path.get('default_img')
                    if env_path:
                        assets_payload.append({
                            "path": env_path,
                            "label": f"Location: {target_env}"
                        })
                    
                    # A. Character Assets
                    char_names = shot_data.get('characters', [])
                    # Use the Clean Map we built earlier to resolve these names
                    # Note: shot_data['characters'] might be full names or nicknames depending on Gemini
                    # But we trust our lookup map to handle the mapping.
                    
                    for c_name in char_names:
                        # Try to resolve via cast map
                        # Logic: Try exact, then try partial
                        asset_path = None
                        
                        # 1. Clean Name Lookup
                        c_key = c_name.strip().split(' ')[0]
                        asset_path = st.session_state.cast_lookup_map.get(c_key)
                        
                        # FIX: Handle Gemini Snake Case ("Shays_boyfriend" -> "Shays")
                        if not asset_path and '_' in c_name:
                             norm_key = c_name.replace('_', ' ').strip().split(' ')[0]
                             fallback_path = st.session_state.cast_lookup_map.get(norm_key)
                             if fallback_path:
                                 c_key = norm_key # Update key for Outfit lookup too
                                 asset_path = fallback_path
                        
                        if asset_path:
                             # 1. CHARACTER FACE
                             assets_payload.append({
                                 "path": asset_path,
                                 "label": f"Cast: {c_name}" # MATCH WORLD BUILDER
                             })
                             
                             # 2. OUTFIT (Lookup from Snapshot)
                             w_snapshot = st.session_state.get('cast_wardrobe_map_snapshot', {})
                             
                             # Robust Lookup: Full Name -> First Name -> Normalized
                             outfit_name = w_snapshot.get(c_name) # 1. Full Name
                             
                             if not outfit_name or outfit_name == "Default":
                                 outfit_name = w_snapshot.get(c_key, "Default") # 2. First Name
                                 
                             # 3. Normalized if needed (already derived c_key might be normalized, but check map again)
                             # Note: c_key was updated above if normalization happened, so step 2 covers it.
                             
                             if outfit_name != "Default":
                                 # Resolve Outfit Path
                                 o_path = outfits_data.get(outfit_name)
                                 if isinstance(o_path, dict): o_path = o_path.get('default_img')
                                 
                                 if o_path and os.path.exists(o_path):
                                     assets_payload.append({
                                         "path": o_path,
                                         "label": f"Outfit for {c_name}: {outfit_name}" # MATCH WORLD BUILDER
                                     })
                    
                    # B. Fallback if no assets found but we have a selection (Force Protag)
                    # Safety Fix: Do not force character on B-Roll shots (3, 6, 9, 12)
                    is_broll = sh_id in [3, 6, 9, 12]
                    
                    if not assets_payload and cast_selection and not is_broll:
                        # Use first selected cast member (Fallback)
                        # Fix: Don't use 'all_cast_opts' which might be unbound if cache hit
                        first_key = cast_selection[0]
                        # Convert Full Key to Clean Key logic
                        base = first_key.split('/')[-1].replace('.png','').replace('.jpg','').strip()
                        c_key = base.split(' ')[0]
                        
                        path = st.session_state.cast_lookup_map.get(c_key)
                        
                        if path:
                             assets_payload.append({
                                 "path": path,
                                 "label": "Main Character"
                             })

                    # Construct Prompt Data with ASSETS
                    p_data = {
                         "positive_prompt": p_text,
                         "negative_prompt": "blurry, low quality, distortion, ugly face",
                         "width": 1024, "height": 576, # 16:9 Cinematic
                         "num_images": 1,
                         "guidance_scale": 7.5,
                         "model_type": "nano", 
                         "checkpoint": None,
                         "assets": assets_payload # <--- THE KEY FIX
                    }
                    
                    # Generate Still
                    # We don't pass char_path legacy arg anymore
                    res = generate_image_from_prompt(p_data, base_out)
                    
                    if res and res.get('status') == 'success':
                        img_path = res['image_path']
                        st.image(img_path, caption=f"Sc{s_id}_Sh{sh_id}")
                        
                        # 2. Video Generation
                        if m_type == "Kling Video":
                            st.write("⚡ Sending to Kling AI...")
                            try:
                                k_client = KlingClient()
                                
                                # Upload Image to S3 to get Public URL
                                with open(img_path, "rb") as f_img:
                                    sanitized_series = series_title.replace(" ", "_")
                                    s3_name = f"series_assets/{sanitized_series}/{ep_title}/sc{s_id}_sh{sh_id}.png"
                                    img_url = upload_file_obj(f_img, object_name=s3_name)
                                
                                if img_url:
                                    # Send to Kling
                                    task = k_client.create_video_from_image(img_url, p_text)
                                    st.success(f"Video Task Started! ID: {task.get('task_id')}")
                                    st.info("Check 'Video Studio' tab later for results.")
                                else:
                                    st.error("Failed to upload image to S3. Skipping video.")
                            except Exception as e:
                                st.error(f"Kling Error: {e}")
                                    
                        elif m_type == "Sora 2 Video":
                            st.write("✨ Sending to Sora 2 (OpenAI)...")
                            try:
                                sora_client = SoraClient()
                                # Reuse Image Upload logic
                                with open(img_path, "rb") as f_img:
                                    sanitized_series = series_title.replace(" ", "_")
                                    s3_name = f"series_assets/{sanitized_series}/{ep_title}/sc{s_id}_sh{sh_id}.png"
                                    img_url = upload_file_obj(f_img, object_name=s3_name)
                                    
                                if img_url:
                                    res_url = sora_client.create_video_from_image(img_url, p_text)
                                    if isinstance(res_url, dict) and "error" in res_url:
                                        st.error(f"Sora Error: {res_url['error']}")
                                    else:
                                        st.success(f"Video Generated! [Link]({res_url})")
                                        st.video(res_url)
                                else: 
                                    st.error("S3 Upload Failed")
                            except Exception as e:
                                st.error(f"Sora Error: {e}")
                                
                    else:
                        st.error(f"Failed to render shot {sh_id}")

                status.update(label="Episode Production Complete!", state="complete")


# ==========================================
# TAB 1.5: WORLD BUILDER
# ==========================================
with tab_world:
    st.markdown("### 🌍 World Builder")
    st.info("Construct complex scenes with multiple characters, props, and specific assets.")
    
    # Load Real Data
    world_db = load_world_db()
    scenarios = get_scenarios()
    
    # Layout
    # Layout: Full Width for Builder
    # Removed "Asset Database" Column as requested
    
    st.markdown("#### 🎬 Scenario Director")
    
    # 0. Import Helper
    # Ideally should be at top, but placing here for context
    try:
        from execution.storyboard_utils import generate_storyboard_prompts
    except ImportError as e:
        st.error(f"Failed to import storyboard utils: {e}")
        def generate_storyboard_prompts(s, c, m): return [f"Error: {e}"]

    # 1. Select Scenario
    with st.container():
        st.markdown('<div class="hub-card">', unsafe_allow_html=True)
        st.markdown("#### 🎬 Scenario Director")
        
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
            st.caption(f"Template: {scenario['template_prompt']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if selected_scenario_key:
        # --- SCENE COMPOSITION UI (Synced with Filesystem) ---
        current_selections = {}
        assets_to_inject = [] # List of {path, label}
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            with st.container():
                st.markdown('<div class="hub-card">', unsafe_allow_html=True)
                st.markdown("##### 👥 Cast & Characters")
                # A. Protagonist (Single Select)
                st.markdown("###### 1. Protagonist")
                protag_opts = get_assets_by_category("characters", user_asset_path)
                protag_key = st.selectbox("Select Protagonist", list(protag_opts.keys()), format_func=lambda x: protag_opts[x].get('name', x) if isinstance(protag_opts[x], dict) else x)  
            
                # Handle both World DB dicts and Filesystem paths
                p_final_path = None
                p_final_name = "Character"

                if protag_key:
                    p_val = protag_opts[protag_key]
                    if isinstance(p_val, dict):
                        # DB Asset
                        p_final_name = p_val['name']
                        p_final_path = p_val.get('default_img')
                    else:
                        # Filesystem Asset
                        p_final_name = protag_key.split('/')[-1]
                        p_final_path = p_val
                
                    current_selections["PROTAGONIST"] = p_final_name

                    # --- NEW: Reference Image Selector (Variant Scanner) ---
                    if p_final_path:
                        # Find parent directory to show variations (FileSystem Only)
                        # Cloud Mode: Variations logic is complex, skipping for now or need S3 scan.
                        # For now, let's just use the selected image.
                        
                        # Only scan if it looks like a local path
                        siblings = []
                        if os.path.exists(p_final_path):
                            char_dir = os.path.dirname(p_final_path)
                            valid_exts = ('.png', '.jpg', '.jpeg', '.webp')
                            siblings = [f for f in os.listdir(char_dir) if f.lower().endswith(valid_exts) and not f.startswith('.')]
                    
                        if siblings:
                            # Show selector
                            # default index is currently selected file
                            current_file = os.path.basename(p_final_path)
                            try:
                                def_idx = siblings.index(current_file)
                            except ValueError:
                                def_idx = 0
                            
                            # Variation UI
                            selected_var = st.selectbox("Select Specific Look", siblings, index=def_idx, key="protag_var")
                            p_final_path = os.path.join(char_dir, selected_var)
                
                    # Update Inject List
                    if p_final_path:
                        assets_to_inject.append({"path": p_final_path, "label": "Main Character"})
                        st.image(p_final_path, width=200, caption="Reference LoRA/Image")

                # --- NEW: Main Character Outfit ---
                st.caption("Main Character Outfit")
                fit_opts = get_assets_by_category("outfits")
                # Filter out generic keys if needed, or keep all
                fit_key = st.selectbox("Select Outfit", ["None"] + list(fit_opts.keys()), key="main_outfit")
                
                if fit_key and fit_key != "None":
                    path = fit_opts[fit_key]
                    if isinstance(path, dict): path = path.get('default_img')
                    
                    # Clean name
                    fit_name = fit_key.split('/')[-1] 
                    if os.path.sep in fit_name: fit_name = os.path.splitext(fit_name)[0]
                    
                    current_selections["OUTFIT"] = fit_name
                    
                    # Add to prompt context + injection
                    assets_to_inject.append({"path": path, "label": f"Outfit: {fit_name}"})
                    if path:
                        st.image(path, caption=fit_name)
                    elif not path:
                         # Text only fallback logic handled by generate_image_nano
                         pass

                # B. Cast (Relations) - Multi Select
                st.markdown("###### 2. Friends & Cast")
                rel_opts = get_assets_by_category("relations") 
                # Note: get_assets_by_category now returns simple dict {name: path} for scanned folders
            
                rel_keys = list(rel_opts.keys())
                selected_rels = st.multiselect("Include People", rel_keys)
            
                rel_names = []
                if selected_rels:
                    st.caption("Selected Cast:")
                    r_cols = st.columns(len(selected_rels))
                    for idx, k in enumerate(selected_rels):
                        path = rel_opts[k]
                         # If from DB it might be a dict
                        if isinstance(path, dict):
                             path = path.get('default_img', '')
                             name = path.get('name', k)
                        else:
                             name = os.path.splitext(k.split('/')[-1])[0]
                    
                        rel_names.append(name)
                        assets_to_inject.append({"path": path, "label": f"Cast: {name}"})
                        with r_cols[idx]:
                            if path:
                                 st.image(path, caption=name)

                if rel_names:
                    current_selections["RELATIONS"] = " and ".join(rel_names)
                
                    # Friend Outfits (Phase 4)
                    st.caption("Selected Cast Outfits:")
                    friend_outfit_details = []
                    f_cols = st.columns(len(selected_rels))
                    for idx, k in enumerate(selected_rels):
                        with f_cols[idx]:
                             # Friend Name
                             f_name = rel_opts[k]['name'] if isinstance(rel_opts[k], dict) else k.split('/')[-1]
                         
                             # Outfit Select for this friend (From Assets)
                             # We use regular outfits_data logic
                             f_fit_opts = get_assets_by_category("outfits")
                             # If empty fall back
                             if not f_fit_opts: f_fit_opts = {"Casual": "", "Chic": ""}
                         
                             f_outfit_key = st.selectbox(f"Outfit for {f_name.split()[0]}", list(f_fit_opts.keys()), key=f"fit_{idx}")
                         
                             # Get clear name and path
                             f_outfit_path = None
                             if isinstance(f_fit_opts[f_outfit_key], dict):
                                 f_outfit_name = f_fit_opts[f_outfit_key]['name']
                                 f_outfit_path = f_fit_opts[f_outfit_key].get('default_img')
                             else:
                                 f_outfit_name = os.path.splitext(f_outfit_key.split('/')[-1])[0]
                                 f_outfit_path = f_fit_opts[f_outfit_key]

                             # Text prompt instruction + Image Asset
                             assets_to_inject.append({"path": f_outfit_path, "label": f"Outfit for {f_name}: {f_outfit_name}"}) 
                             friend_outfit_details.append(f"{f_name} in {f_outfit_name}") 
                         
                             # VISUAL PREVIEW
                             # VISUAL PREVIEW
                             if f_outfit_path:
                                 st.image(f_outfit_path, width=150, caption=f_outfit_name)
                             else:
                                 st.caption(f"No preview: {f_outfit_name}")
                    
                    if friend_outfit_details:
                        current_selections["FRIEND_OUTFITS"] = ", ".join(friend_outfit_details)
                else:
                    current_selections["RELATIONS"] = "nobody"

                st.markdown('</div>', unsafe_allow_html=True)
        # --- RIGHT COLUMN: CONTEXT ---
        with col_c2:
            with st.container():
                st.markdown('<div class="hub-card">', unsafe_allow_html=True)
                st.markdown("##### 📍 Setting & Props")

                # C. Pets
                st.markdown("###### 3. Pets")
                pet_opts = get_assets_by_category("pets")
                selected_pets = st.multiselect("Include Pets", list(pet_opts.keys()))
                
                pet_names = []
                if selected_pets:
                    p_cols = st.columns(len(selected_pets))
                    for idx, k in enumerate(selected_pets):
                        path = pet_opts[k]
                        name = k.split('/')[-1]
                        pet_names.append(name)
                        assets_to_inject.append({"path": path, "label": f"Pet: {name}"})
                        with p_cols[idx]:
                             if path:
                                 st.image(path, caption=name)
                
                st.divider()
                
                # D. Props & Vehicles
                st.markdown("###### 4. Props & Vehicles")
                prop_opts = get_assets_by_category("props")
                veh_opts = get_assets_by_category("vehicles")
                all_props = {**prop_opts, **veh_opts}
                
                selected_props = st.multiselect("Include Items", list(all_props.keys()))
                prop_names = []
                if selected_props:
                     # Limit preview columns
                     pr_cols = st.columns(min(len(selected_props), 4))
                     for idx, k in enumerate(selected_props):
                         path = all_props[k]
                         name = k.split('/')[-1]
                         prop_names.append(name)
                         assets_to_inject.append({"path": path, "label": f"Prop: {name}"})
                         
                         col_idx = idx % 4
                         with pr_cols[col_idx]:
                             if path:
                                 st.image(path, caption=name)

                if prop_names:
                    current_selections["PROPS"] = ", ".join(prop_names)
                    current_selections["VEHICLE"] = prop_names[0]
                else:
                    current_selections["PROPS"] = "props"
                    current_selections["VEHICLE"] = "vehicle"
                
                st.divider()

                # E. Location
                st.markdown("###### 5. Location")
                loc_opts = get_assets_by_category("locations")
                loc_key = st.selectbox("Select Location", ["None"] + list(loc_opts.keys()))
                
                if loc_key and loc_key != "None":
                      val = loc_opts[loc_key]
                      path = val['default_img'] if isinstance(val, dict) else val
                      
                      # Clean name
                      loc_name = loc_key.split('/')[-1]
                      if os.path.sep in loc_name: loc_name = os.path.splitext(loc_name)[0]
                      
                      current_selections["LOCATION"] = loc_name
                      assets_to_inject.append({"path": path, "label": "Location"})
                      
                      
                      if path:
                          st.image(path, caption=loc_name, width=300) # Added Thumbnail
                else:
                      current_selections["LOCATION"] = "generic location"

                st.markdown('</div>', unsafe_allow_html=True)
        
        # V3.9: Wrapped in Form to prevent Camera Settings Reload Loop
        with st.form(key="wb_camera_form"):
            # --- CAMERA CONTROLS ---
            with st.expander("🎥 Camera & Scene Settings", expanded=False):
                col_cam, col_light, col_action = st.columns(3)
                with col_cam:
                    st.markdown("**📸 Hardware**")
                    sel_camera = st.selectbox("Camera Type", ["Auto"] + knowledge_base.get("cameras", []), key="wb_cam")
                    sel_lens = st.selectbox("Lens", ["Auto"] + knowledge_base.get("lenses", []), key="wb_lens")
                    sel_shot = st.selectbox("Shot Type", ["Auto", "Close Up", "Medium Shot", "Full Body", "Wide Shot", "Extreme Close Up", "Cowboy Shot", "Overhead"], key="wb_shot") 
                    sel_ar = st.selectbox("Aspect Ratio", ["9:16", "16:9", "4:5", "1:1", "3:2"], index=0, key="wb_ar")
    
    
                with col_light:
                    st.markdown("**💡 Lighting & Mood**")
                    sel_lighting = st.selectbox("Lighting", ["Auto"] + knowledge_base.get("lighting", []), key="wb_light")
                    sel_weather = st.selectbox("Weather", ["Auto"] + knowledge_base.get("weather", []), key="wb_weath")
                    sel_film_stock = st.selectbox("Film Stock", ["Auto"] + knowledge_base.get("film_stocks", []), key="wb_stock")
    
                with col_action:
                    st.markdown("**🎬 Direction**")
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
            st.markdown("#### 📝 Creative Direction")
            custom_details = st.text_area("Specific Details / Custom Context", placeholder="e.g. Holding a red cup, Laughing uniquely, Cyberpunk neon colors...", help="These details will be added to the prompt.")
    
            # --- PROMPT GENERATION LOGIC UPDATE ---
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
    
            # --- AI DIRECTOR BUTTON ---
            col_ai_btn, col_blank = st.columns([1, 1])
            with col_ai_btn:
                # FORM SUBMIT BUTTON 1
                run_director = st.form_submit_button("✨ AI Director: Rewrite & Enhance", help="Uses the World-Class Brain to rewrite this into a masterpiece.")
            
            if run_director:
                with st.spinner("Director is rewriting scene..."):
                    # 1. Identify Main Assets & Extras
                    main_char_path = None
                    main_outfit_path = None
                    extras_payload = []
                    
                    for asset in assets_to_inject:
                        lbl = asset.get('label', '')
                        path = asset.get('path')
                        
                        if "Main Character" in lbl:
                             main_char_path = path
                        elif lbl.startswith("Outfit: "): # Exact main outfit label format
                             main_outfit_path = path
                        else:
                             # Friends, Friend Outfits, Pets, Props
                             extras_payload.append(asset)
                    
                    st.toast(f"Brain Analyzing: Main + {len(extras_payload)} Extra Assets...")
    
                    # 2. Call Generator with full context
                    # We treat the current draft as 'additional_notes' context
                    enhanced_res = generate_prompt_content(
                        vibe=current_selections.get("VIBE", "luxury"),
                        outfit=current_selections.get("OUTFIT", "fashion"),
                        character=main_char_path, # Pass the PATH
                        outfit_path=main_outfit_path, # Pass the PATH
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
                        
                        additional_notes=f"REWRITE THIS SCENE to be cinematic, high-fashion, and detailed. Keep the character consistent: {final_prompt}",
                        model_engine="gpt-4o"
                    )
                    
                    if enhanced_res and "positive_prompt" in enhanced_res:
                        # final_prompt = enhanced_res["positive_prompt"] <--- REMOVED to prevent conflict with change detector
                        st.session_state['wb_manual_prompt'] = enhanced_res["positive_prompt"]
                        st.toast("Prompt Upgraded by AI Director!")
                        # Force refresh
                        # We won't rerun, checking if session state key helps below
    
            # --- STATE MANAGEMENT FOR PROMPT BOX ---
            # We need the box to update when:
            # 1. Dropdowns change (Calculated prompt changes)
            # 2. AI Button is clicked (AI rewrites prompt)
            # 3. User types (Manual edit)
            
            # Store calculated prompt to detect dropdown changes
            if 'last_calculated_prompt' not in st.session_state:
                st.session_state['last_calculated_prompt'] = final_prompt
            
            # Check for dropdown changes (Auto-update box if logic changes)
            if final_prompt != st.session_state['last_calculated_prompt']:
                 st.session_state['wb_manual_prompt'] = final_prompt
                 st.session_state['last_calculated_prompt'] = final_prompt
            
            # Initialize key if needed
            if 'wb_manual_prompt' not in st.session_state:
                 st.session_state['wb_manual_prompt'] = final_prompt
    
            # Make Prompt Editable
            final_prompt_val = st.text_area("Final Prompt (Editable)", key="wb_manual_prompt", height=200)
            final_prompt = final_prompt_val
            
            st.markdown("<br>", unsafe_allow_html=True)
            # FORM SUBMIT BUTTON (Generate)
            gen_world = st.form_submit_button("Generate Single Scene", type="primary", use_container_width=True)

    # --- ACTION AREA (Outside Form) ---
    st.divider()
    col_act1, col_act2 = st.columns(2)
    
    with col_act1:
        st.markdown("#### 📸 Quick Shot")
        
        # Generation Logic triggered by Form Submit
        if gen_world:
             can_proceed = True
             if st.session_state.get("authenticated"):
                 username = st.session_state.current_user.get("username")
                 if not auth_mgr.deduct_credits(username, 1):
                     st.error("❌ Not enough credits!")
                     can_proceed = False
                 else:
                     st.toast("🪙 1 Credit Deducted")
             
             if can_proceed:
                 with st.spinner("Generating..."):
                     wb_payload = {
                         "positive_prompt": final_prompt,
                         "aspect_ratio": sel_ar, 
                         "model_type": "nano", 
                         "assets": assets_to_inject
                     }
                     res = generate_image_from_prompt(wb_payload, get_user_out_dir("World"))
                     
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
                         st.toast("🪙 Credit Refunded")

        # Display Result (Persistent)
        if 'wb_last_img' in st.session_state and os.path.exists(st.session_state['wb_last_img']):
            last_img = st.session_state['wb_last_img']
            st.image(last_img, caption="World Build Result", use_container_width=True)
            
            with open(last_img, "rb") as f:
                st.download_button("⬇️ Download Image", f, file_name=os.path.basename(last_img), mime="image/png")
    
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
                if st.button("🎬 Generate All 4 Shots"):
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
                if st.button("🚀 Add Storyboard to Campaign Queue", type="primary"):
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
                 with st.spinner("Generating with Nano Multimodal..."):
                     # Construct Payload
                     wb_payload = {
                         "positive_prompt": final_prompt,
                         "aspect_ratio": "4:5", # Default for social
                         "model_type": "nano", # Force Nano for multi-ref
                         "assets": assets_to_inject # New Field
                     }
                     
                     res = generate_image_from_prompt(wb_payload, get_user_out_dir("World"))
                     
                     if res["status"] == "success":
                         st.image(res["image_path"], caption="World Build Result")
                     else:
                         st.error(f"Failed: {res.get('logs')}")


# ==========================================
# ==========================================
# TAB 2: CAMPAIGN MANAGER (Renamed from Tab 3)
# ==========================================
with tab_campaign:
    st.markdown("### Campaign Job Queue")
    
    # 1. Status Dashboard
    queue = campaign_mgr.queue
    pending_count = campaign_mgr.get_pending_count()
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
    for i, job in enumerate(queue):
        col_q_info, col_q_del = st.columns([6, 1])
        
        with col_q_info:
            with st.expander(f"{'DONE' if job['status']=='completed' else 'WAITING'} {job['name']} ({job['status']})"):
                st.write(f"**Description:** {job['description']}")
                st.write(f"**Created:** {job['created_at']}")
                if job['status'] == 'completed':
                    st.write("**Results:**")
                    cols = st.columns(4)
                    if 'results' in job:
                         for idx, res in enumerate(job['results']):
                             if res and res.get("image_path"):
                                 cols[idx % 4].image(res["image_path"], width=100)
        
        with col_q_del:
            # Only allow deleting pending or completed tasks, not running ones (to match index)
            if st.button("DEL", key=f"del_job_{i}", help="Delete this task"):
                campaign_mgr.remove_job(i)
                st.rerun()

# ==========================================
# TAB 4: VIDEO STUDIO
# ==========================================
with tab_video:
    st.markdown("### AI Video Generator (Kling 2.6 / Veo 2.0)")
    st.info("Transform your generated images into high-motion video clips using the latest 2026 models.")
    
    # Sub-tabs for Creation vs Gallery
    v_tab_create, v_tab_gallery = st.tabs(["✨ Generate Video", "📚 Video Gallery (Recover)"])
    
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
                     
                     with st.expander(f"🎬 {vid}", expanded=True):
                         c1, c2 = st.columns([3, 1])
                         with c1:
                             st.video(vid_path)
                         with c2:
                             st.markdown("**Actions**")
                             with open(vid_path, "rb") as vf:
                                 st.download_button(
                                     f"⬇️ Download",
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
                    with st.expander("⚙️ Advanced Model Settings (Override)", expanded=False):
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
                    with st.expander("🎥 Camera & Motion Control", expanded=False):
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
                    st.markdown("**🕺 Video Driven Motion**")
                    
                    m_tab1, m_tab2 = st.tabs(["🔗 URL Input", "📤 Upload Video"])
                    
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
                with st.spinner("Analyzing Image Context & Physics..."):
                    # Save temp for analysis
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
with tab_char:
    st.markdown("### 👤 Character Studio")
    st.info("Design your cast with precision. Used consistently across the platform.")

    col_char_ctrl, col_char_view = st.columns([1, 1.5]) 
    
    with col_char_ctrl:
        with st.container(border=True):
            st.markdown("#### 🛠️ Design Specs")
            
            with st.form("character_creator_form"):
                # 1. Reference Image
                st.markdown("**1. Reference (Optional)**")
                ref_img = st.file_uploader("Upload Face/Reference", type=['png', 'jpg', 'jpeg'])
                
                # 2. Output Mode
                st.markdown("**2. Output Format**")
                output_mode = st.selectbox("Generation Mode", ["Concept Portrait (Vertical)", "Character Sheet (7-Angle Views)"])
                
                st.divider()
                
                # 3. Attributes
                st.markdown("**3. Attributes**")
                
                with st.expander("👤 Core Identity", expanded=True):
                    c_gender = st.selectbox("Gender", ["Female", "Male", "Non-Binary"])
                    eth_opts = [
                        "Any",
                        "African American", "East Asian (Korean/Japanese)", "Southeast Asian", 
                        "South Asian (Indian)", "Middle Eastern", "Mediterranean", 
                        "Northern European", "Eastern European", "Latino/Hispanic", 
                        "Indigenous", "Mixed Race", "Afro-Latina", "Nordic"
                    ]
                    c_ethnicity = st.selectbox("Ethnicity", eth_opts)
                    c_age = st.slider("Age", 18, 90, 25)
                

                with st.expander("💇‍♀️ Face & Details", expanded=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        c_hair_col = st.selectbox("Hair Color", ["Any", "Blonde", "Brunette", "Black", "Red", "Platinum", "Pastel Pink", "Grey", "White"])
                        c_eye = st.selectbox("Eye Color", ["Any", "Blue", "Green", "Brown", "Hazel", "Grey", "Amber"])
                        c_tat_style = st.selectbox("Tattoo Style", ["None", "Minimalist", "Traditional", "Tribal", "Geometric", "Full Sleeve", "Henna", "Face Tats"])
                    with c2:
                        c_hair_style = st.selectbox("Hair Style", ["Any", "Long Straight", "Wavy", "Curly", "Bob Cut", "Pixie", "Braids", "Messy Bun", "Ponytail", "Buzz Cut", "Afro", "Dreads"])
                        c_facial = st.selectbox("Facial Hair", ["None", "Stubble", "Beard", "Goatee", "Mustache", "Clean Shaven"])
                        c_tat_place = st.multiselect("Tattoo Placement", ["Arms", "Chest", "Neck", "Back", "Face", "Legs", "Lower Back"])
                    
                    c_makeup = st.selectbox("Makeup", ["None", "Natural", "Minimal", "Soft Glam", "Heavy Glam", "Goth", "Vintage"])
                    c_skin = st.multiselect("Skin Details", ["Freckles", "Beauty Marks", "Vitiligo", "Tattoos", "Scarring", "Perfect Skin", "Textured Skin", "Wrinkles"])

                with st.expander("💪 Body Composition", expanded=False):
                    st.caption("Customize physique details (0-100)")
                    c_body = st.slider("General Physique", 0, 100, 50, help="0: Skinny | 50: Athletic | 100: Heavy/Curvy")
                    c_muscle = st.slider("Muscle Mass", 0, 100, 20, help="0: Soft | 100: Ripped Bodybuilder")
                    
                    # Bust Details
                    c1, c2 = st.columns([2, 1]) 
                    with c1:
                         c_bust = st.slider("Bust Size", 0, 100, 40, help="Applies to Femme characters")
                    with c2:
                         c_bust_type = st.selectbox("Bust Type", ["Natural / Drop", "Perky / Athletic", "Augmented / Implants"])
                    
                    c_waist = st.slider("Waist Width", 0, 100, 50, help="0: Cinematic Hourglass | 100: Wide")
                    c_hips = st.slider("Hips Width", 0, 100, 50, help="0: Narrow | 100: Exaggerated Shelf Hips")
                    
                    # Glute Details
                    c3, c4 = st.columns([2, 1])
                    with c3:
                        c_glutes = st.slider("Glute Size", 0, 100, 50, help="0: Flat | 100: Exaggerated Bubble Butt")
                    with c4:
                        c_glute_type = st.selectbox("Glute Type", ["Soft / Natural", "Athletic / Hard", "BBL / Surgical"])

                # Name
                st.divider()
                st.markdown("**4. Finalize**")
                char_name = st.text_input("Character Name", placeholder="e.g. Sarah")
                
                # Submit
                st.markdown("<br>", unsafe_allow_html=True)
                create_char = st.form_submit_button("✨ Generate Character", type="primary", use_container_width=True)

    with col_char_view:
        st.markdown("#### 📸 Studio Preview")
        
        # State Handling
        if create_char:
            if not char_name:
                st.error("Please name your character first.")
            else:
                # Build Prompt
                attrs = {
                   "gender": c_gender,
                   "ethnicity": c_ethnicity,
                   "age": c_age,
                   "body_type": c_body,
                   "muscle": c_muscle,
                   "bust": c_bust,
                   "bust_type": c_bust_type,
                   "waist": c_waist,
                   "hips": c_hips,
                   "glutes": c_glutes,
                   "glute_type": c_glute_type,
                   "hair_color": c_hair_col,
                   "hair_style": c_hair_style,
                   "eye_color": c_eye,
                   "facial_hair": c_facial,
                   "makeup": c_makeup,
                   "skin_details": c_skin,
                   "tattoo_style": c_tat_style,
                   "tattoo_places": c_tat_place
                }
                st.session_state['char_last_attrs'] = attrs 
                
                base_prompt = build_character_prompt(attrs)
                
                if output_mode == "Character Sheet (7-Angle Views)":
                    full_prompt = get_character_sheet_prompt(base_prompt)
                    ar = "16:9" # Sheets need width
                    target_w, target_h = 1344, 768
                else:
                    full_prompt = base_prompt
                    ar = "4:5" # Portrait
                    target_w, target_h = 896, 1152
                
                st.success("Prompt Built!")
                with st.expander("View Prompt"):
                    st.code(full_prompt)
                
                # Generate
                user = st.session_state.current_user.get("username")
                if auth_mgr.deduct_credits(user, 1):
                    with st.spinner("Creating Character in Studio..."):
                         # Check for Identity Lock Reference
                         assets = []
                         if st.session_state.get("lock_identity_path"):
                             assets.append({
                                 "path": st.session_state["lock_identity_path"],
                                 "label": f"Cast: {char_name or 'Main'}"
                             })
                         
                         # Payload
                         payload = {
                             "positive_prompt": full_prompt,
                             "width": target_w, "height": target_h,
                             "model_type": "nano",
                             "assets": assets
                         }
                         
                         res = generate_image_from_prompt(payload, get_user_out_dir("Characters/Concepts"))
                         
                         if res["status"] == "success":
                             st.session_state['char_preview'] = res['image_path']
                             st.session_state['char_final_prompt'] = full_prompt
                             st.toast("Character Generated!")
                         else:
                             auth_mgr.add_credits(user, 1) # Refund
                             st.error(f"Failed: {res.get('logs')}")
                else:
                    st.error("Not enough credits.")

        # Display Result
        if 'char_preview' in st.session_state:
            preview_path = st.session_state['char_preview']
            st.image(preview_path, caption="Concept Preview", use_container_width=True)
            
            # Save Actions
            c_save, c_sheet = st.columns(2)
            with c_save:
                if st.button("💾 Save as New Asset", use_container_width=True):
                     if char_name:
                         # Move to User Assets
                         user = st.session_state.current_user.get("username")
                         asset_dir = os.path.join("output", "users", user, "Assets", "Characters", char_name)
                         os.makedirs(asset_dir, exist_ok=True)
                         
                         # Copy Image
                         new_path = os.path.join(asset_dir, "default.png")
                         import shutil
                         shutil.copy(preview_path, new_path)
                         
                         # Create Metadata
                         details = {
                             "name": char_name,
                             "prompt": st.session_state.get('char_final_prompt', ''),
                             "created": str(datetime.datetime.now())
                         }
                         with open(os.path.join(asset_dir, "details.json"), "w") as f:
                             json.dump(details, f)
                             
                         st.success(f"Saved {char_name} to Assets!")
                         # Clear Cache
                         st.cache_data.clear()
                         time.sleep(1)
                         st.rerun()
                     else:
                         st.error("Enter a name in the form.")
            
            with c_sheet:
                if st.button("🔒 Lock & Create Sheet", use_container_width=True, type="secondary"):
                    st.session_state["lock_identity_path"] = preview_path
                    st.session_state["trigger_lock_sheet"] = True
                    st.rerun()

        # Handle Triggered Lock Sheet
        if st.session_state.get("trigger_lock_sheet"):
            st.session_state["trigger_lock_sheet"] = False # Reset
            
            attrs = st.session_state.get("char_last_attrs")
            if attrs:
                from execution.character_utils import build_character_prompt, get_character_sheet_prompt
                base_prompt = build_character_prompt(attrs)
                full_prompt = get_character_sheet_prompt(base_prompt)
                target_w, target_h = 1344, 768
                
                user = st.session_state.current_user.get("username")
                if auth_mgr.deduct_credits(user, 1):
                    with st.spinner("Locking Identity and Creating Sheet..."):
                        assets = [{
                            "path": st.session_state["lock_identity_path"],
                            "label": f"Cast: {char_name or 'Main'}"
                        }]
                        payload = {
                            "positive_prompt": full_prompt,
                            "width": target_w, "height": target_h,
                            "model_type": "nano",
                            "assets": assets
                        }
                        res = generate_image_from_prompt(payload, get_user_out_dir("Characters/Concepts"))
                        if res["status"] == "success":
                            st.session_state['char_preview'] = res['image_path']
                            st.session_state['char_final_prompt'] = full_prompt
                            st.toast("Identity Locked & Sheet Created!")
                            st.rerun()
                        else:
                            auth_mgr.add_credits(user, 1)
                            st.error("Failed to generate sheet.")
