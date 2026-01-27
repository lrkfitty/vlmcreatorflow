
import streamlit as st
import os
import json
from execution.magic_ui import card_begin, card_end
from execution.character_utils import build_character_prompt
from execution.generate_image import generate_image_from_prompt, parse_script_to_scenes
from execution.load_assets import get_assets_by_category
from execution.kling_client import KlingClient
from execution.sora_client import SoraClient
from execution.s3_uploader import upload_file_obj

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
                    base_out = os.path.join(get_user_out_dir_func("Series"), series_title.replace(" ", "_"), ep_title)
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
                        
                        # 1. Reuse Logic to Re-Construct Assets Payload 
                        # (We could have stored it, but reconstructing ensures fresh state)
                        assets_payload = []
                        
                        # Environment Injection
                        target_env = shot_data['environment']
                        # Override logic same as UI
                        if shot_data['scene_id'] in [2, 4]: # Rough B-Roll logic approximation or use shot_data
                             pass # Rely on what was passed in shot_data['environment'] which IS the target env
                        
                        env_path = vibes_data.get(target_env) or assets.get('locations', {}).get(target_env)
                        if isinstance(env_path, dict): env_path = env_path.get('default_img')
                        if env_path:
                            assets_payload.append({
                                "path": env_path,
                                "label": f"Location: {target_env}"
                            })
                        
                        # Character Assets
                        char_names = shot_data.get('characters', [])
                        for c_name in char_names:
                            # 1. Clean Name Lookup
                            c_key = c_name.strip().split(' ')[0]
                            asset_path = st.session_state.cast_lookup_map.get(c_key)
                            
                            if not asset_path and '_' in c_name:
                                 norm_key = c_name.replace('_', ' ').strip().split(' ')[0]
                                 fallback_path = st.session_state.cast_lookup_map.get(norm_key)
                                 if fallback_path:
                                     c_key = norm_key
                                     asset_path = fallback_path
                            
                            if asset_path:
                                 assets_payload.append({
                                     "path": asset_path,
                                     "label": f"Cast: {c_name}"
                                 })
                                 
                                 # 2. Outfit
                                 w_snapshot = st.session_state.get('cast_wardrobe_map_snapshot', {})
                                 outfit_name = w_snapshot.get(c_name)
                                 if not outfit_name or outfit_name == "Default":
                                     outfit_name = w_snapshot.get(c_key, "Default")
                                     
                                 if outfit_name != "Default":
                                     o_path = outfits_data.get(outfit_name)
                                     if isinstance(o_path, dict): o_path = o_path.get('default_img')
                                     if o_path and os.path.exists(o_path):
                                         assets_payload.append({
                                             "path": o_path,
                                             "label": f"Outfit for {c_name}: {outfit_name}"
                                         })

                        # Construct Prompt Data
                        p_data = {
                             "positive_prompt": p_text,
                             "negative_prompt": "blurry, low quality, distortion, ugly face",
                             "width": 1024, "height": 576,
                             "num_images": 1,
                             "guidance_scale": 7.5,
                             "model_type": "nano", 
                             "assets": assets_payload 
                        }
                        
                        # Generate Still
                        res = generate_image_from_prompt(p_data, base_out)
                        
                        if res and res.get('status') == 'success':
                            img_path = res['image_path']
                            st.image(img_path, caption=f"Sc{s_id}_Sh{sh_id}")
                            
                            # 2. Video Generation
                            if m_type == "Kling Video":
                                st.write("⚡ Sending to Kling AI...")
                                try:
                                    k_client = KlingClient()
                                    with open(img_path, "rb") as f_img:
                                        sanitized_series = series_title.replace(" ", "_")
                                        s3_name = f"series_assets/{sanitized_series}/{ep_title}/sc{s_id}_sh{sh_id}.png"
                                        img_url = upload_file_obj(f_img, object_name=s3_name)
                                    
                                    if img_url:
                                        task = k_client.create_video_from_image(img_url, p_text)
                                        st.success(f"Video Task Started! ID: {task.get('task_id')}")
                                    else:
                                        st.error("Failed to upload image to S3.")
                                except Exception as e:
                                    st.error(f"Kling Error: {e}")
                                        
                            elif m_type == "Sora 2 Video":
                                st.write("✨ Sending to Sora 2 (OpenAI)...")
                                try:
                                    sora_client = SoraClient()
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
    """
    Renders the Mini Series Studio UI.
    """
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
            
            # Use Unified Asset Loader
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
            
            # V3: Hollywood Camera Controls - Restored & Expanded
            with st.expander("🎥 Cinematography Settings", expanded=False):
                c_cam, c_lens = st.columns(2)
                with c_cam:
                     cam_opts = [
                         "Auto", 
                         "Arri Alexa 65 (Large Format)", "Arri Alexa Mini LF", "Sony Venice 2 (8K)", 
                         "RED V-Raptor [VV]", "Panavision Millennium DXL2", 
                         "IMAX 15/70mm Film", "Kodak Vision3 35mm Film", "16mm Bolex", "Super 8mm",
                         "iPhone 15 Pro Max (ProRes)", "VHS Camcorder (90s)", "CCTV Security Cam"
                     ]
                     s_camera = st.selectbox("Camera Body", cam_opts)
                     
                     stock_opts = [
                         "Auto", 
                         "Kodak Portra 400", "Kodak Portra 800", "Fujifilm Velvia 100", 
                         "Cinestill 800T (Halation)", "Kodak Tri-X 400 (B&W)", "Ilford HP5 (Grainy B&W)",
                         "Technicolor (3-Strip)", "Bleach Bypass (Gritty)"
                     ]
                     s_film_stock = st.selectbox("Film Stock / LUT", stock_opts)

                with c_lens:
                     lens_opts = [
                         "Auto", 
                         "Arri Signature Prime", "Cooke S4/i Prime", "Panavision Primo 70", "Canon K-35 Vintage",
                         "Atlas Orion Anamorphic", "Laowa Probe Lens",
                         "14mm Ultra Wide", "24mm Wide", "35mm Standard", "50mm Standard", 
                         "85mm Portrait", "105mm Macro", "200mm Telephoto", "600mm Sniper"
                     ]
                     s_lens = st.selectbox("Lens Glass", lens_opts)

                     grade_opts = ["Auto", "Teal & Orange (Blockbuster)", "Vintage Warmth", "Cool Blue", "Noir B&W", "Matrix Green", "Euphoria Purple"]
                     s_filter_look = st.selectbox("Color Grade", grade_opts)
                
                c_light, c_style = st.columns(2)
                with c_light:
                     light_opts = ["Auto", "Golden Hour", "Studio Softbox", "Rembrandt", "Neon Cyberpunk", "Natural Diffused", "Hard Flash", "Silhouette", "God Rays"]
                     s_lighting = st.selectbox("Lighting", light_opts)
                with c_style:
                     style_opts = [
                         "Auto", 
                         "Wes Anderson (Symmetrical/Pastel)", "Christopher Nolan (IMAX/Cold)", "Denis Villeneuve (Brutalist)",
                         "Wong Kar-wai (Step Printing)", "Quentin Tarantino (Low Angle)", 
                         "Euphoria (Glitter/A24)", "Cyberpunk (Neon)", "1950s Technicolor", "1990s Sitcom"
                     ]
                     s_movie_style = st.selectbox("Style Reference", style_opts)
            
            s_transition_style = st.selectbox("Transition Pacing", ["Standard", "Fast / TikTok", "Slow / Cinematic", "Match Cut"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_director = st.form_submit_button("✨ Director Vision AI", type="primary", use_container_width=True)

    if submit_director:
            if not series_script:
                st.error("Please enter a synopsis.")
            elif not cast_selection:
                st.error("Please select a cast.")
            else:
                with st.spinner("AI Director is breaking down the script..."):
                    # 1. Clean Cast Names & Map
                    char_opts = get_assets_by_category("characters", user_asset_path)
                    rel_opts = get_assets_by_category("relations", user_asset_path)
                    all_cast_opts = {**char_opts, **rel_opts}
                    
                    clean_cast_map = {} 
                    clean_names_list = []
                    
                    for full_key in cast_selection:
                        c_data = all_cast_opts.get(full_key)
                        real_path = None
                        if isinstance(c_data, dict):
                            real_path = c_data.get('default_img')
                        else:
                            real_path = c_data
                            
                        base = full_key.split('/')[-1].replace('.png','').replace('.jpg','').strip()
                        clean_name = base.split(' ')[0]
                        
                        if real_path:
                            clean_cast_map[clean_name] = real_path
                            clean_names_list.append(clean_name)
                    
                    st.session_state.cast_lookup_map = clean_cast_map

                    # Clean Roles Map
                    clean_roles_map = {}
                    if cast_role_map:
                        for full_key, role in cast_role_map.items():
                            base = full_key.split('/')[-1].replace('.png','').replace('.jpg','').strip()
                            c_name = base.split(' ')[0]
                            clean_roles_map[c_name] = role

                    # Clean Wardrobe Map
                    clean_wardrobe_map = {}
                    director_refs = [] 
                    
                    if cast_wardrobe_map:
                        for full_key, outfit in cast_wardrobe_map.items():
                            base = full_key.split('/')[-1].replace('.png','').replace('.jpg','').strip()
                            c_name = base.split(' ')[0]
                            clean_wardrobe_map[c_name] = outfit
                            clean_wardrobe_map[base] = outfit 
                            
                            if outfit != "Default":
                                o_path = outfits_data.get(outfit)
                                if isinstance(o_path, dict): o_path = o_path.get('default_img')
                                if o_path:
                                    director_refs.append({
                                        "path": o_path, 
                                        "label": f"{base}'s Wardrobe: {outfit}"
                                    })
                        
                        st.session_state.cast_wardrobe_map_snapshot = clean_wardrobe_map
                    
                    for c_name, c_path in clean_cast_map.items():
                         director_refs.append({
                             "path": c_path,
                             "label": f"Cast Member: {c_name}"
                         })

                    # V2 API Call
                    sb_data = parse_script_to_scenes(
                        script_text=series_script, 
                        cast_list=clean_names_list, 
                        environment_name=series_env,
                        genre=s_genre,
                        tone=s_tone,
                        roles_map=clean_roles_map,
                        wardrobe_map=clean_wardrobe_map,
                        ref_images=director_refs,
                        secondary_environment=sec_env,
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
                        # clear keys
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
        
        generated_shots_data = [] 
        
        # Ensure lookup map
        if "cast_lookup_map" not in st.session_state:
             char_opts = get_assets_by_category("characters", user_asset_path)
             rel_opts = get_assets_by_category("relations", user_asset_path)
             all_cast_opts = {**char_opts, **rel_opts}
             
             clean_cast_map = {}
             if cast_selection:
                 for full_key in cast_selection:
                    c_data = all_cast_opts.get(full_key)
                    real_path = c_data.get('default_img') if isinstance(c_data, dict) else c_data
                    
                    base = full_key.split('/')[-1].replace('.png','').replace('.jpg','')
                    clean_name = base.split(' ')[0]
                    if real_path: clean_cast_map[clean_name] = real_path
                 st.session_state.cast_lookup_map = clean_cast_map
        
        cast_map = st.session_state.cast_lookup_map

        for scene_idx, scene in enumerate(sb.get('scenes', [])):
            with st.container():
                st.markdown(f"#### Scene {scene.get('id')}: {scene.get('location')}")
                
                shots = scene.get('shots', [])
                for shot_idx, shot in enumerate(shots):
                    key_base = f"s{scene_idx}_sh{shot_idx}"
                    
                    # Resolve Character
                    char_list = shot.get('characters', [])
                    char_ref_name = char_list[0] if char_list else None
                    char_full_key = None
                    
                    if char_ref_name:
                        char_full_key = cast_map.get(char_ref_name)
                        if not char_full_key:
                            for c_name, c_key in cast_map.items():
                                if c_name in char_ref_name or char_ref_name in c_name:
                                    char_full_key = c_key
                                    break
                    
                    if not char_full_key and cast_selection and not (shot_idx+1 in [3,6,9,12]):
                         char_full_key = cast_selection[0]

                    col_txt, col_img = st.columns([1.5, 1])
                    
                    # Fix NameError by initializing motion_type
                    motion_type = "Still" 
                    mocap_file = None

                    with col_txt:
                        st.markdown(f"**Shot {shot_idx+1}**")
                        
                        meta_cols = st.columns(4)
                        meta_cols[0].caption(f"📏 {shot.get('shot_size', 'Auto')}")
                        meta_cols[1].caption(f"🎥 {shot.get('camera_angle', 'Auto')}")
                        meta_cols[2].caption(f"💡 {shot.get('lighting_type', 'Auto')}")
                        meta_cols[3].caption(f"🎨 {shot.get('composition', 'Auto')}")
                        
                        all_cast_keys = list(st.session_state.cast_lookup_map.keys())
                        current_chars = shot.get('characters', [])
                        valid_defaults = []
                        for c in current_chars:
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
                        shot['characters'] = selected_chars
                        
                        time_opts = ["Morning", "Noon", "Afternoon", "Golden Hour", "Blue Hour", "Night", "Midnight"]
                        ai_time = shot.get('time_of_day', 'Day')
                        ai_time_norm = ai_time.title() if ai_time else "Day"
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
                        shot['time_of_day'] = selected_time

                        trans_opts = ["None"] + knowledge_base.get("transitions", [])
                        sel_trans = st.selectbox("Transition", trans_opts, key=f"trans_{key_base}", label_visibility="collapsed")
                        shot['transition'] = sel_trans
                        
                        shot_prompt = st.text_area("Visual Prompt", value=shot.get('visual_prompt'), height=250, key=f"p_{key_base}", label_visibility="collapsed")
                        st.caption(f"Length: {len(shot_prompt) if shot_prompt else 0} chars (Target: 800+)")
                        
                        c_gen, c_type = st.columns([1, 1.5])
                        with c_gen:
                            if st.button(f"Generate Shot {shot_idx+1}", key=f"btn_{key_base}"):
                                user = st.session_state.current_user.get("username")
                                if not auth_mgr.deduct_credits(user, 1):
                                    st.error("❌ No Credits!")
                                else:
                                    with st.spinner("Rolling camera..."):
                                        final_assets_payload = []
                                        
                                        # Resolve Cast Assets (Robust)
                                        target_chars = shot.get('characters', [])
                                        # If empty and not B-Roll, force first cast
                                        is_broll = (shot_idx + 1) in [3, 6, 9, 12]
                                        if not target_chars and cast_selection and not is_broll:
                                             # Fallback protagonist
                                             pass 

                                        for raw_name in target_chars:
                                            c_path = st.session_state.cast_lookup_map.get(raw_name)
                                            if c_path:
                                                final_assets_payload.append({"path": c_path, "label": f"Cast: {raw_name}"})
                                                # Outfit
                                                w_snapshot = st.session_state.get('cast_wardrobe_map_snapshot', {})
                                                o_key = w_snapshot.get(raw_name, "Default")
                                                if o_key != "Default":
                                                    o_path = outfits_data.get(o_key)
                                                    if isinstance(o_path, dict): o_path = o_path.get('default_img')
                                                    if o_path: final_assets_payload.append({"path": o_path, "label": f"Outfit: {o_key}"})

                                        # Location
                                        target_env = sec_env if is_broll and sec_env != "None" else series_env
                                        env_path = vibes_data.get(target_env) or assets.get('locations', {}).get(target_env)
                                        if isinstance(env_path, dict): env_path = env_path.get('default_img')
                                        if env_path: final_assets_payload.append({"path": env_path, "label": f"Location: {target_env}"})
                                        
                                        # Prompt
                                        time_setting = shot.get('time_of_day', 'Day')
                                        trans_setting = shot.get('transition', 'None')
                                        trans_text = f"Visual Transition Style: {trans_setting}. " if trans_setting and trans_setting != "None" else ""
                                        final_shot_prompt = f"Time of Day: {time_setting}. {trans_text}{shot_prompt}"
                                        
                                        p_data = {
                                             "positive_prompt": final_shot_prompt,
                                             "model_type": "nano", 
                                             "assets": final_assets_payload,
                                             "aspect_ratio": "16:9"
                                        }
                                        
                                        res = generate_image_from_prompt(p_data, get_user_out_dir_func("Series"))
                                        if res["status"] == "success":
                                            st.session_state[f"img_{key_base}"] = res["image_path"]
                                            st.success("Shot Captured!")
                                        else:
                                            st.error(f"Error: {res.get('logs')}")
                        
                        with c_type:
                            motion_type = st.radio("Media", ["Still", "Kling Video", "Sora 2 Video", "Mocap"], key=f"m_{key_base}", horizontal=True, label_visibility="collapsed")
                            if motion_type == "Mocap":
                                mocap_file = st.file_uploader("Ref", type=['mp4'], key=f"up_{key_base}", label_visibility="collapsed")

                    with col_img:
                        if f"img_{key_base}" in st.session_state:
                            img_p = st.session_state[f"img_{key_base}"]
                            st.image(img_p, caption=f"Shot {shot_idx+1}", use_container_width=True)
                            if os.path.exists(img_p):
                                with open(img_p, "rb") as file:
                                    st.download_button("⬇️", file, file_name=os.path.basename(img_p), mime="image/png", key=f"dl_{key_base}")
                        else:
                            st.info("No Image")
                    
                    st.divider()

                    generated_shots_data.append({
                        "scene_id": scene.get('id'),
                        "shot_id": shot_idx + 1,
                        "prompt": shot_prompt,
                        "type": motion_type, # Fixed scope
                        "mocap": mocap_file,
                        "characters": shot.get('characters'),
                        "environment": series_env,
                        "transition": shot.get('transition'),
                        "generated_still": st.session_state.get(f"img_{key_base}") 
                    })
