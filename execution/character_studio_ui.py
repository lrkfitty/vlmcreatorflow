
import streamlit as st
import os
import json
import time
import datetime
import shutil
from execution.magic_ui import card_begin, card_end, circular_progress
from execution.character_utils import build_character_prompt, get_character_sheet_prompt
from execution.generate_image import generate_image_from_prompt
from load_assets import promote_image_to_asset
from execution.auth import auth_mgr
from execution.s3_uploader import upload_file_obj

def render_character_studio(characters_data, get_user_out_dir_func, campaign_mgr=None):
    """
    Renders the Character Studio UI.
    args:
        characters_data: Dictionary of character assets.
        get_user_out_dir_func: Function to get user output directory.
    """
    col_char_ctrl, col_char_view = st.columns([1, 1.5]) 
    
    with col_char_ctrl:
        card_begin()
        
        # Initialize user early to prevent UnboundLocalError in save block
        user = st.session_state.current_user.get("username") if st.session_state.get("current_user") else "guest"

        st.markdown("#### Design Specs")
        
        with st.form("character_creator_form"):
            # 1. Reference Image
            st.markdown("**1. Reference (Optional)**")
            ref_img = st.file_uploader("Upload Face/Reference", type=['png', 'jpg', 'jpeg'])
            
            # UNIFIED: Add Reference Identity from Library
            st.caption("Or choose existing Identity:")
            # Use base 'characters_data' (Unified)
            char_keys = sorted(list(characters_data.keys()))
            ref_identity = st.selectbox("Base on Character", ["None"] + char_keys, 
                                        format_func=lambda x: characters_data[x].get('name', x) if isinstance(characters_data.get(x), dict) else x)
            
            # Logic to use ref_identity path if selected and no upload
            lock_identity_path = None
            if ref_identity != "None":
                 val = characters_data[ref_identity]
                 lock_identity_path = val.get('default_img') if isinstance(val, dict) else val
                 st.caption(f"Using Identity: {ref_identity.split('/')[-1]}")
            
            # Pass this to session state for generation
            if lock_identity_path:
                st.session_state['lock_identity_path'] = lock_identity_path
            elif 'lock_identity_path' in st.session_state:
                del st.session_state['lock_identity_path']
            
            # 2. Output Mode
            st.markdown("**2. Output Format**")
            output_mode = st.selectbox("Generation Mode", ["Concept Portrait (Vertical)", "Character Sheet (7-Angle Views)"])
            
            st.divider()
            
            # 3. Attributes
            st.markdown("**3. Attributes**")
            
            with st.expander("Core Identity", expanded=True):
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
            

            with st.expander("Face & Details", expanded=False):
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

            with st.expander("Body Composition", expanded=False):
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
            col_q, col_sub = st.columns([1, 2])
            with col_q:
                add_to_queue = st.checkbox("Add to Queue", value=False)
            with col_sub:
                create_char = st.form_submit_button("✨ Generate Character", type="primary", use_container_width=True)
            
        card_end()

    with col_char_view:
        card_begin()
        st.markdown("#### Studio Preview")
        
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
                    ar = "4:5" # User requested 4:5 for all Studio generations
                    target_w, target_h = 896, 1152
                else:
                    full_prompt = base_prompt
                    ar = "4:5" # Portrait
                    target_w, target_h = 896, 1152
                
                st.success("Prompt Built!")
                with st.expander("View Prompt"):
                    st.code(full_prompt)
                
                # Generate
                if add_to_queue and campaign_mgr:
                     # QUEUE MODE
                     job_name = f"Char_{char_name}"
                     
                     # Check for Identity Lock Reference
                     assets = []
                     if st.session_state.get("lock_identity_path"):
                         assets.append({
                             "path": st.session_state["lock_identity_path"],
                             "label": f"Cast: {char_name or 'Main'}"
                         })
                         
                     campaign_mgr.add_job(
                        name=job_name,
                        description=f"Character Concept: {char_name}",
                        prompt_data={
                             "positive_prompt": full_prompt,
                             "width": target_w, "height": target_h,
                             "aspect_ratio": ar,
                             "model_type": "nano",
                             "assets": assets
                        },
                        settings={"batch_count": 1},
                        output_folder=get_user_out_dir_func("Characters/Concepts"),
                        char_path=st.session_state.get("lock_identity_path")
                     )
                     st.success(f"✅ Added '{char_name}' to Campaign Queue!")
                     
                else:
                    # SYNC MODE
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
                                 "aspect_ratio": ar,
                                 "model_type": "nano",
                                 "assets": assets
                             }
                             
                             res = generate_image_from_prompt(payload, get_user_out_dir_func("Characters/Concepts"))
                             
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
                if st.button("Save as New Asset", use_container_width=True):
                     if char_name:
                         # Use Unified Helper
                         res_save = promote_image_to_asset(
                             preview_path, 
                             user, 
                             "Characters", 
                             char_name, 
                             st.session_state.get('char_final_prompt', '')
                         )
                         
                         if res_save["status"] == "success":
                             st.success(f"Saved {char_name} to Assets!")
                             st.info(res_save.get("logs", ""))
                             # Clear Cache
                             st.cache_data.clear()
                             time.sleep(1)
                             st.rerun()
                         else:
                             st.error(f"Save Failed: {res_save.get('error')}")
                     else:
                         st.error("Enter a name in the form.")
            
            with c_sheet:
                if st.button("Lock & Create Sheet", use_container_width=True, type="secondary"):
                    st.session_state["lock_identity_path"] = preview_path
                    st.session_state["trigger_lock_sheet"] = True
                    st.rerun()

        # Handle Triggered Lock Sheet
        if st.session_state.get("trigger_lock_sheet"):
            st.session_state["trigger_lock_sheet"] = False # Reset
            
            attrs = st.session_state.get("char_last_attrs")
            if attrs:
                # Re-import not needed as we imported at top
                base_prompt = build_character_prompt(attrs)
                full_prompt = get_character_sheet_prompt(base_prompt)
                target_w, target_h = 1344, 768
                
                user = st.session_state.current_user.get("username")
                if auth_mgr.deduct_credits(user, 1):
                    prog_ph = st.empty()
                    # from execution.magic_ui import circular_progress
                    with prog_ph.container():
                         circular_progress()
                         st.caption("Creating in Studio...")
                         
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
                    res = generate_image_from_prompt(payload, get_user_out_dir_func("Characters/Concepts"))
                    if res["status"] == "success":
                        st.session_state['char_preview'] = res['image_path']
                        st.session_state['char_final_prompt'] = full_prompt
                        st.toast("Identity Locked & Sheet Created!")
                        st.rerun()
                    else:
                        auth_mgr.add_credits(user, 1)
                        st.error("Failed to generate sheet.")
        card_end()
