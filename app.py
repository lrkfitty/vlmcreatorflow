import streamlit as st
import sys
import os
import json

# Add execution directory to path to import scripts
sys.path.append(os.path.join(os.path.dirname(__file__), 'execution'))

try:
    from load_assets import load_assets
    from generate_prompt import generate_prompt_content
    from generate_image import generate_image_from_prompt
    from campaign_runner import CampaignManager
    from execution.generate_video import generate_video_kling
    from execution.s3_uploader import upload_file_obj
    from generate_video_prompt import generate_motion_prompt
    from world_manager import load_world_db, get_assets_by_category, get_scenarios
except ImportError as e:
    st.error(f"Error importing scripts: {e}")
    st.stop()

st.set_page_config(page_title="CreateFlow | Viral Lens Media", layout="wide", page_icon=None)

# --- AUTHENTICATION GATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_app_password():
    pwd = st.session_state.get("auth_input", "")
    # Default password is 'admin' if env not set
    if pwd == os.getenv("APP_PASSWORD", "admin"): 
        st.session_state.authenticated = True
    else:
        st.error("⛔ Incorrect Password")

if not st.session_state.authenticated:
    st.markdown("## 🔒 Access Restricted")
    st.text_input("Enter Access Code", type="password", key="auth_input", on_change=check_app_password)
    st.info("Default code: `admin` (Set APP_PASSWORD in .env to change)")
    st.stop()

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

# HEADER
st.markdown("<div class='brand-overline'>Viral Lens Media</div>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center'>CreateFlow</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 3rem;'>Enterprise-Grade Content Workflow</p>", unsafe_allow_html=True)

# Load Assets
try:
    assets = load_assets()
    vibes_data = assets.get('vibes', {})
    outfits_data = assets.get('outfits', {})
    characters_data = assets.get('characters', {})
    
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
# def scan_models(): ...

# --- TABS LAYOUT# TABS
tab_wizard, tab_world, tab_campaign, tab_video = st.tabs([
    "Workflow Wizard", 
    "World Builder",
    "Campaign Queue", 
    "Video Studio"
])

# ==========================================
# TAB 1: WORKFLOW WIZARD (Existing Logic)
# ==========================================
with tab_wizard:
    st.markdown("### Step-by-Step Content Creator")
    
    # --- UI Inputs ---
    col_vibe, col_outfit, col_char = st.columns(3)
    
    with col_vibe:
        st.markdown("**1. Select Vibe**")
        selected_vibe_name = st.selectbox("Choose Aesthetic", vibes_list)
        if selected_vibe_name:
            st.image(vibes_data[selected_vibe_name], use_container_width=True)
            
    with col_outfit:
        st.markdown("**2. Select Outfit**")
        selected_outfit_name = st.selectbox("Choose Outfit", outfits_list)
        if selected_outfit_name:
            st.image(outfits_data[selected_outfit_name], use_container_width=True)

    with col_char:
        st.markdown("**3. Select Character**")
        selected_character_name = st.selectbox("Choose Model", characters_list)
        if selected_character_name:
            st.image(characters_data[selected_character_name], use_container_width=True)

    st.divider()

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
            
        with col_action:
            st.markdown("**Action**")
            sel_action = st.selectbox("Subject Action", ["Auto"] + knowledge_base.get("actions", []))
            sel_emotion = st.selectbox("Emotion", ["Auto"] + knowledge_base.get("emotions", []))

    # Custom Direction
    st.subheader("4. Creative Direction")
    custom_scenario = st.text_input("Scenario / Context", placeholder="e.g. At a luxury coffee shop in Paris...")
    custom_notes = st.text_area("Specific Details", placeholder="Enter any extra details here...")
    
    col_imgs, col_model, col_like = st.columns(3)
    
    with col_model:
        prompt_engine = st.selectbox("Brain (Prompt Engine)", ["gpt-4o", "gemini-1.5-pro"], key="wiz_brain")
        # New: Render Engine Selector
        st.info("🧠 Brain: " + prompt_engine)
        render_engine = "nano" # Force Cloud Engine
        # render_engine = st.selectbox("Painter (Image Engine)", ["nano", "sd_local"], index=0, help="Use 'sd_local' for unrestricted generation.", key="wiz_painter")
        
    with col_like:
        likeness = 0.5 
        # Hidden for Nano
        pass

    with col_imgs:
        # This slider is ONLY for the immediate Wizard Generation button
        num_images = st.slider("Test Count (Wizard Only)", min_value=1, max_value=4, value=1, key="wiz_test_count")
        
        selected_checkpoint = None
        # SD Local Checkpoint Logic Removed for Cloud Deployment

    # --- CAMPAIGN BUTTON ---
    col_c_btn, col_c_batch = st.columns([3, 1])
    with col_c_batch:
        campaign_batch = st.number_input("Queue Copies", min_value=1, max_value=10, value=1, help="How many variations to queue?")

    with col_c_btn:
        if st.button("Add to Campaign Queue"):
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
                aspect_ratio=sel_ar.split(" ")[0], 
                model_engine=prompt_engine 
            )
            
            prompt_data["likeness_strength"] = likeness # Pass to generator
            
            prompt_data["model_type"] = render_engine 
            prompt_data["checkpoint"] = selected_checkpoint # Pass the model file 
            
            job_name = f"{selected_outfit_name} - {clean_val(selected_vibe_name)}"
            campaign_mgr.add_job(
                name=job_name,
                description=f"Engine: {render_engine} | Checked: {selected_checkpoint if render_engine=='sd_local' else 'N/A'}",
                prompt_data=prompt_data,
                settings={ "batch_count": campaign_batch },
                output_folder="output",
                char_path=char_path,
                outfit_path=outfit_path,
                vibe_path=vibe_path
            )
            msg = f"Added '{job_name}'! (Engine: {render_engine}, Batch: {campaign_batch})"
            st.success(msg)
            if render_engine == 'sd_local':
                st.toast(f"Checkpoint: {selected_checkpoint}")

    st.divider()

    if st.button("Generate Content (Wizard)", type="primary", use_container_width=True):
        with st.status(f"Running workflow ({prompt_engine} + {render_engine})...", expanded=True) as status:
            st.write("🧠 **Step 1:** Generating Master Prompt...")
            
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
                aspect_ratio=sel_ar.split(" ")[0], 
                model_engine=prompt_engine 
            )
            
            prompt_data["likeness_strength"] = likeness # Pass to generator
            
            st.json(prompt_data, expanded=False)
            st.write(f"Step 2: Generating {num_images} Image(s)...")
            
            # Parallel Execution
            from concurrent.futures import ThreadPoolExecutor
            results = []
            
            with ThreadPoolExecutor() as executor:
                # Correctly pass the model via the data dict
                prompt_data["model_type"] = render_engine 
                prompt_data["checkpoint"] = selected_checkpoint 
                # CRITICAL: Pass the image paths so SD Local can see them
                futures = [executor.submit(generate_image_from_prompt, prompt_data, "output", char_path, outfit_path, vibe_path) for i in range(num_images)]
                for future in futures:
                    results.append(future.result())
            
            # Display Results
            cols = st.columns(num_images)
            for i, result in enumerate(results):
                with cols[i]:
                    if result and result.get("status") == "success":
                        st.image(result["image_path"], caption=f"Variant {i+1}")
                        st.success("Saved")
                    else:
                        st.error("Failed")
                        if result: st.write(result)
            
            status.update(label="Workflow Complete!", state="complete", expanded=True)



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
                protag_opts = get_assets_by_category("characters")
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
                # User Provided Emotions (30 List)
                emotions = [
                    "Auto", "Confident", "Carefree", "Playful", "Relaxed", "Flirty", "Happy", "Calm", "Curious", 
                    "Focused", "Content", "Empowered", "Soft", "Radiant", "Unbothered", "Dreamy", 
                    "Joyful", "Peaceful", "Excited", "Serene", "Bold", "Mischievous", "Warm", 
                    "Self-assured", "Chill", "Lighthearted", "Magnetic", "Present", "Satisfied", 
                    "Quietly happy", "Seductive", "Boss Bitch", "Hysterical", "Zen" # Kept a few custom ones too
                ]
                sel_emotion = st.selectbox("Emotion", emotions, key="wb_emo")

            with col_action:
                st.markdown("**🎬 Direction**")
                sel_film = st.selectbox("Film Style", ["Auto"] + knowledge_base.get("styles", []), key="wb_film")
                sel_angle = st.selectbox("Angle", ["Auto", "Low Angle", "High Angle (Drone)", "Dutch Angle", "Close Up", "Wide Shot", "Over-the-Shoulder", "Selfie Angle", "POV"], key="wb_ang")
                # User Provided Actions (30 List)
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
        
        st.info(f"**Base Context:** {custom_scenario[:100]}...")
        
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
            if st.button("✨ AI Director: Rewrite & Enhance", help="Uses the World-Class Brain to rewrite this into a masterpiece."):
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
        # Binding to session state key ensures values persist and updates flow correctly
        final_prompt_val = st.text_area("Final Prompt (Editable)", key="wb_manual_prompt", height=200)
        
        # Use the value from the box for everything downstream
        final_prompt = final_prompt_val
        
        # --- ACTION AREA ---

        # --- ACTION AREA ---
        st.divider()
        col_act1, col_act2 = st.columns(2)
        
        with col_act1:
            st.markdown("#### 📸 Quick Shot")
            
            # DEBUG: view payload
            with st.expander("debug payload"):
                st.write(assets_to_inject)
            
            if st.button("Generate Single Scene", type="primary"):
                 with st.spinner("Generating..."):
                     wb_payload = {
                         "positive_prompt": final_prompt,
                         "aspect_ratio": sel_ar, # Use User Selection
                         "model_type": "nano", 
                         "assets": assets_to_inject
                     }
                     res = generate_image_from_prompt(wb_payload, "output")
                     
                     with st.expander("Generation Logs", expanded=False):
                         st.code(res.get("logs", "No logs"))
                         
                     if res["status"] == "success":
                         st.image(res["image_path"])
                         with open(res["image_path"], "rb") as f:
                             st.download_button("⬇️ Download Image", f, file_name=os.path.basename(res["image_path"]), mime="image/png")
        
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
                         with st.spinner(f"Generating Shot {i+1}..."):
                             wb_payload = {
                                 "positive_prompt": p + f", {final_prompt}", # Append full context
                                 "aspect_ratio": sel_ar, 
                                 "model_type": "nano", 
                                 "assets": assets_to_inject
                             }
                             res = generate_image_from_prompt(wb_payload, "output")
                             if res["status"] == "success":
                                 st.toast(f"Shot {i+1} Generated!")
                                 st.session_state[f"sb_img_{i}"] = res["image_path"] # Saved!
                             else:
                                 st.error(f"Shot {i+1} Failed")

                for i, p in enumerate(prompts):
                    col_sb_text, col_sb_img = st.columns([2, 1])
                    
                    with col_sb_text:
                        val = st.text_area(f"Shot {i+1}", value=p, height=100, key=f"sb_{i}")
                        edited_prompts.append(val)
                        
                        if st.button(f"Generate Shot {i+1}", key=f"btn_sb_{i}"):
                            with st.spinner("Rolling camera..."):
                                wb_payload = {
                                     "positive_prompt": val, # Use edited text
                                     "aspect_ratio": sel_ar, 
                                     "model_type": "nano", 
                                     "assets": assets_to_inject
                                 }
                                res = generate_image_from_prompt(wb_payload, "output")
                                with st.expander(f"Logs Shot {i+1}", expanded=False):
                                     st.code(res.get("logs", "No logs"))
                                     
                                if res["status"] == "success":
                                    st.session_state[f"sb_img_{i}"] = res["image_path"]
                                else:
                                    st.error(res["logs"])
                    
                    with col_sb_img:
                        if f"sb_img_{i}" in st.session_state:
                             img_path = st.session_state[f"sb_img_{i}"]
                             st.image(img_path)
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
                    if 'campaign_queue' not in st.session_state:
                        st.session_state['campaign_queue'] = []
                    
                    # Capture current assets state
                    # Must use deepcopy or list to avoid reference issues
                    import copy
                    current_assets = copy.deepcopy(assets_to_inject)
                    
                    for p in edited_prompts:
                        job = {
                            "prompt": p,
                            "aspect_ratio": sel_ar,
                            "model": "nano", 
                            "count": 1,
                            "assets": current_assets # Use fixed assets
                        }
                        st.session_state['campaign_queue'].append(job)
                    
                    st.success(f"Added {len(edited_prompts)} shots to Campaign Queue! Go to 'Campaign Queue' tab to run them.")

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
                     
                     res = generate_image_from_prompt(wb_payload, "output")
                     
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
        st.markdown("#### Generated Videos (Cloud Container)")
        if not os.path.exists("output"):
             st.warning("No output folder found.")
        else:
             # Find MP4s
             videos = [f for f in os.listdir("output") if f.endswith(".mp4")]
             videos.sort(key=lambda x: os.path.getmtime(os.path.join("output", x)), reverse=True)
             
             if not videos:
                 st.info("No videos found yet.")
             else:
                 for vid in videos:
                     vid_path = os.path.join("output", vid)
                     
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
        col_v_in, col_v_set = st.columns([1, 1])
    
    with col_v_in:
        st.markdown("**1. Select Input Image**")
        # Allow uploading OR selecting from recent outputs (mockup for now)
        video_source_img = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        
        if video_source_img:
            st.image(video_source_img, caption="Input Preview", use_container_width=True)
        
        st.markdown("**2. Motion Settings**")
        col_mv, col_phy = st.columns(2)
        with col_mv:
            vid_movement = st.selectbox("Camera Move", ["Auto", "Pan Left", "Pan Right", "Zoom In", "Zoom Out", "Handheld", "Drone Orbit"], key="vid_move")
        with col_phy:
            vid_physics = st.selectbox("Physics Focus", ["Standard", "High Physics", "Jiggle Physics", "Water/Liquids"], help="Enforce specific physics simulations.")
            
        motion_prompt = st.text_area("Motion Prompt", height=100, placeholder="Describe the movement...")
        
        if st.button("Auto-Generate with Vision AI"):
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
            st.caption(f"Suggested: {st.session_state['motion_suggestion']}")
            if st.button("Use Suggestion"):
                motion_prompt = st.session_state['motion_suggestion'] 
                # Note: streamlit text_area update is tricky without key, but user can copy paste for now
                st.code(motion_prompt)

    with col_v_set:
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

        audio_enabled = st.checkbox("Enable Audio (Sound FX)", value=False)
        
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
                 # Size Check
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
        
        st.divider()
        
        if st.button("Generate Video", type="primary"):
            if not video_source_img:
                st.error("Please upload an image first.")
            elif not (os.getenv("KLING_ACCESS_KEY") and os.getenv("KLING_SECRET_KEY")):
                st.error("Missing KLING_ACCESS_KEY or KLING_SECRET_KEY in .env file.")
            else:
                with st.status("Generating Video...", expanded=True) as status:
                    st.write(f"Sending to Kling AI 2.6 API ({mode_val.upper()} Mode)...")
                    
                    # Save uploaded file momentarily
                    temp_path = os.path.join("output", "temp_video_input.png")
                    with open(temp_path, "wb") as f:
                        f.write(video_source_img.getbuffer())
                        
                    st.write("Processing... (Standard: ~2-5m, Pro: ~5-10m)")
                    # Pass the selected mode
                    result = generate_video_kling(
                        temp_path, 
                        motion_prompt, 
                        duration=5, 
                        model_version=model_version_input, 
                        quality_mode=mode_val, 
                        camera_control=camera_data,
                        ref_video_path=ref_video_url,
                        ref_orientation=ref_orientation
                    )

                    # Common Result Handling
                    if result["status"] == "success":
                        status.update(label="Complete!", state="complete")
                        
                        if result.get("warning"):
                             st.warning(result["warning"])
                             st.caption(f"Task ID: {result.get('task_id')}")
                        else:
                             st.success(f"Video Generated! (Task ID: {result.get('task_id')})")
                        
                        if result.get('video_path'):
                             st.success(f"💾 Saved to: {result['video_path']}")
                             
                        if result.get('video_url'):
                            st.write(f"**Direct Link:** [Click to Open]({result.get('video_url')})")
                            st.video(result.get('video_url'))
                            
                            # Add Download Button using local container file
                            if result.get('video_path') and os.path.exists(result['video_path']):
                                with open(result['video_path'], "rb") as v_file:
                                    st.download_button(
                                        label="⬇️ Download MP4",
                                        data=v_file,
                                        file_name=os.path.basename(result['video_path']),
                                        mime="video/mp4"
                                    )
                        else:
                            st.warning(f"Video URL not found. Use Task ID {result.get('task_id')} to fetch manually.")
                            
                        with st.expander("Process Logs", expanded=False):
                            st.write(result.get("logs", []))
                    else:
                        status.update(label="Failed", state="error")
                        st.error(f"Error: {result.get('error')}")
                        with st.expander("Error Logs", expanded=True):
                             st.write(result.get("logs", []))
