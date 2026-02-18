"""
Multi-Shot Character Reference Generator

Generates multiple angles of a character from a single reference image.
"""

import streamlit as st
from execution.character_utils import get_character_sheet_prompt
from execution.generate_image import generate_image_from_prompt
from execution.auth import auth_mgr
import os
import google.generativeai as genai

def render_multishot_ui(get_user_out_dir_func):
    """
    Renders the Multi-Shot reference generator UI.
    
    Args:
        get_user_out_dir_func: Function to get user output directory
    """
    st.markdown("### Multi-Shot Reference Generator")
    st.info("Upload a character reference and generate multiple angles for consistency across your content.")
    
    # --- Character & Outfit Reference Dropdowns ---
    assets_data = st.session_state.get("global_assets", {})
    characters_data = assets_data.get("characters", {}).copy()
    characters_data.update(assets_data.get("relations", {}))  # Include friends
    outfits_data = assets_data.get("outfits", {})
    
    char_list = ["None (use uploaded reference only)"] + sorted(characters_data.keys())
    outfit_list = ["None"] + sorted(outfits_data.keys())
    
    st.markdown("**🎭 Character & Outfit Reference**")
    ref_col1, ref_col2 = st.columns(2)
    with ref_col1:
        selected_char = st.selectbox(
            "Character Reference",
            char_list,
            index=0,
            help="Select a character from your asset library for identity consistency",
            key="ms_char_select"
        )
    with ref_col2:
        selected_outfit = st.selectbox(
            "Outfit Reference",
            outfit_list,
            index=0,
            help="Select an outfit for wardrobe consistency",
            key="ms_outfit_select"
        )
    
    # Resolve paths
    char_ref_path = characters_data.get(selected_char) if selected_char != "None (use uploaded reference only)" else None
    outfit_ref_path = outfits_data.get(selected_outfit) if selected_outfit != "None" else None
    
    # Show thumbnails if selected
    if char_ref_path or outfit_ref_path:
        thumb_cols = st.columns(2)
        with thumb_cols[0]:
            if char_ref_path:
                st.image(char_ref_path, caption=selected_char, width=120)
        with thumb_cols[1]:
            if outfit_ref_path:
                st.image(outfit_ref_path, caption=selected_outfit, width=120)
    
    st.divider()
    
    # --- Mode Selection (OUTSIDE form so it reruns instantly) ---
    st.markdown("**1. Output Format**")
    multishot_mode = st.selectbox(
        "Generation Mode",
        [
            "Character Sheet (4 Angles)", 
            "Individual Shots (Batch)", 
            "Single Custom Angle",
            "End Frame Generator"
        ],
        key="multishot_mode_select"
    )
    
    # Mode-specific options (also outside form for instant reactivity)
    selected_angles = []
    custom_angle = ""
    endframe_description = ""
    transition_style = "Moderate"
    endframe_ar = "16:9"
    
    if multishot_mode == "Individual Shots (Batch)":
        angle_opts = [
            "Front View",
            "Side View (Left)",
            "Side View (Right)",
            "3/4 View (Left)",
            "3/4 View (Right)",
            "Back View",
            "Over Shoulder",
            "Low Angle",
            "High Angle"
        ]
        selected_angles = st.multiselect(
            "Select Angles to Generate",
            angle_opts,
            default=["Front View", "Side View (Left)", "3/4 View (Left)", "Back View"]
        )
    elif multishot_mode == "Single Custom Angle":
        custom_angle = st.text_input(
            "Describe the Angle/Pose",
            placeholder="e.g. looking over shoulder, confident expression"
        )
    elif multishot_mode == "End Frame Generator":
        st.markdown("🎬 **Cinematic End Frame** — Describe how the scene should end")
        endframe_description = st.text_area(
            "End Frame Description",
            placeholder="e.g. character turns away from camera, walking into a sunset, dramatic silhouette",
            height=100,
            help="Describe what changes between the start frame and end frame",
            key="endframe_desc_input"
        )
        
        # --- AI Director Vision Button ---
        if st.button("🎬 AI Director Vision", help="AI analyzes your start frame and suggests an end frame", key="ai_director_btn"):
            # Check if there's a start frame in session from a previous upload
            temp_path = os.path.join("output", "temp_multishot_ref.png")
            if os.path.exists(temp_path):
                with st.spinner("🎬 Director is analyzing your start frame..."):
                    try:
                        google_key = os.getenv("GOOGLE_API_KEY")
                        if not google_key:
                            st.error("Missing GOOGLE_API_KEY for AI Director.")
                        else:
                            genai.configure(api_key=google_key)
                            model = genai.GenerativeModel("gemini-2.0-flash")
                            
                            from PIL import Image
                            start_img = Image.open(temp_path)
                            
                            # Build context
                            extra_context = additional_prompt if additional_prompt else ""
                            
                            director_prompt = (
                                "You are an AWARD-WINNING CINEMATOGRAPHER analyzing a START FRAME from a shot.\n\n"
                                "TASK: Suggest what the END FRAME of this same shot should look like.\n\n"
                                "Analyze the image and describe:\n"
                                "1. What cinematic movement should happen (camera pan, dolly, zoom, etc.)\n"
                                "2. How the subject's pose/position should change\n"
                                "3. How the lighting/mood should evolve\n"
                                "4. What makes this transition feel cinematic and emotionally impactful\n\n"
                                "OUTPUT: Write ONLY the end frame description in 2-3 sentences. "
                                "Be specific and visual. No JSON, no labels — just the description.\n"
                            )
                            if extra_context:
                                director_prompt += f"\nCONTEXT FROM USER: {extra_context}\n"
                            
                            response = model.generate_content([director_prompt, start_img])
                            suggestion = response.text.strip()
                            
                            st.session_state["ai_director_suggestion"] = suggestion
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"AI Director Error: {e}")
            else:
                st.warning("⚠️ Upload a start frame image first (click Generate once to save it), then try AI Director.")
        
        # Show AI Director suggestion if available
        if st.session_state.get("ai_director_suggestion"):
            st.success(f"🎬 **Director's Vision:** {st.session_state['ai_director_suggestion']}")
            if st.button("✅ Use This Description", key="use_director_suggestion"):
                st.session_state["endframe_desc_input"] = st.session_state["ai_director_suggestion"]
                del st.session_state["ai_director_suggestion"]
                st.rerun()
            if st.button("🔄 Get Another Suggestion", key="retry_director"):
                del st.session_state["ai_director_suggestion"]
                st.rerun()
        
        ef_col1, ef_col2 = st.columns(2)
        with ef_col1:
            transition_style = st.selectbox(
                "Transition Intensity",
                ["Subtle", "Moderate", "Dramatic"],
                index=1,
                help="How much the end frame can deviate from the start frame"
            )
        with ef_col2:
            endframe_ar = st.selectbox(
                "Aspect Ratio",
                ["16:9", "4:5", "1:1", "9:16"],
                index=0,
                help="Cinematic 16:9 recommended"
            )
    
    st.divider()
    
    # Additional prompts (outside form)
    additional_prompt = st.text_area(
        "Additional Details (Optional)",
        placeholder="e.g. wearing black jacket, cyberpunk aesthetic, neon lighting",
        height=80,
        help="Add specific details you want to maintain across all angles",
        key="multishot_additional"
    )
    
    st.divider()
    
    # --- Form: just the image upload + generate button ---
    with st.form("multishot_form"):
        st.markdown("**📸 Upload Reference Image**")
        ref_upload = st.file_uploader(
            "Character or Object Reference", 
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear reference image of your character or object"
        )
        
        if ref_upload:
            st.image(ref_upload, caption="Reference Preview", use_container_width=True)
        
        col_q, col_gen = st.columns([1, 2])
        with col_q:
            add_to_queue = st.checkbox("Add to Queue", value=False)
        with col_gen:
            generate_multishot = st.form_submit_button("✨ Generate Multi-Shot", type="primary", use_container_width=True)
    
    # Processing Logic
    if generate_multishot:
        if not ref_upload:
            st.error("Please upload a reference image first.")
        else:
            user = st.session_state.current_user.get("username") if st.session_state.get("current_user") else "guest"
            
            # Save uploaded file temporarily
            temp_ref_path = os.path.join("output", "temp_multishot_ref.png")
            os.makedirs("output", exist_ok=True)
            with open(temp_ref_path, "wb") as f:
                f.write(ref_upload.getbuffer())
            
            # Build base prompt
            base_prompt = "character maintaining exact identity and features from reference image"
            if additional_prompt:
                base_prompt += f", {additional_prompt}"
            
            # Build common asset list with character/outfit references
            def build_assets_list(start_frame_path, label="Reference Character"):
                """Builds the asset payload with character/outfit refs."""
                asset_list = [{"path": start_frame_path, "label": label}]
                # Extract character name for outfit pairing
                char_name = None
                if char_ref_path:
                    char_name = selected_char.replace("(My) ", "")
                    asset_list.append({"path": char_ref_path, "label": f"Cast: {char_name}"})
                if outfit_ref_path:
                    outfit_label = f"Outfit for {char_name}" if char_name else f"Outfit: {selected_outfit}"
                    asset_list.append({"path": outfit_ref_path, "label": outfit_label})
                return asset_list
            
            # Handle different modes
            if multishot_mode == "Character Sheet (4 Angles)":
                # Generate 4-angle character sheet
                full_prompt = get_character_sheet_prompt(base_prompt)
                
                # Credit check
                if auth_mgr.deduct_credits(user, 1):
                    with st.spinner("Generating 4-angle character sheet..."):
                        assets = build_assets_list(temp_ref_path)
                        payload = {
                            "positive_prompt": full_prompt,
                            "aspect_ratio": "16:9",
                            "model_type": "nano",
                            "assets": assets
                        }
                        
                        res = generate_image_from_prompt(payload, get_user_out_dir_func("MultiShot"))
                        
                        if res["status"] == "success":
                            st.session_state['multishot_result'] = res['image_path']
                            st.success("✅ Character sheet generated!")
                            st.rerun()
                        else:
                            auth_mgr.add_credits(user, 1)  # Refund
                            st.error(f"Generation failed: {res.get('logs')}")
                else:
                    st.error("Not enough credits.")
            
            elif multishot_mode == "Individual Shots (Batch)":
                # Generate each angle separately
                if not selected_angles:
                    st.error("Please select at least one angle.")
                else:
                    # Credit check for batch
                    total_credits_needed = len(selected_angles)
                    if auth_mgr.deduct_credits(user, total_credits_needed):
                        st.session_state['multishot_batch_results'] = []
                        
                        for angle in selected_angles:
                            with st.spinner(f"Generating {angle}..."):
                                angle_prompt = f"{base_prompt}, {angle.lower()}, professional photography"
                                
                                assets = build_assets_list(temp_ref_path)
                                payload = {
                                    "positive_prompt": angle_prompt,
                                    "aspect_ratio": "4:5",
                                    "model_type": "nano",
                                    "assets": assets
                                }
                                
                                res = generate_image_from_prompt(payload, get_user_out_dir_func("MultiShot"))
                                
                                if res["status"] == "success":
                                    st.session_state['multishot_batch_results'].append({
                                        "angle": angle,
                                        "path": res['image_path']
                                    })
                                    st.toast(f"✅ {angle} complete!")
                                else:
                                    st.error(f"{angle} failed: {res.get('logs')}")
                                    auth_mgr.add_credits(user, 1)  # Refund this one
                        
                        st.success("Batch generation complete!")
                        st.rerun()
                    else:
                        st.error(f"Need {total_credits_needed} credits for this batch.")
            
            elif multishot_mode == "Single Custom Angle":
                if not custom_angle:
                    st.error("Please describe the angle/pose you want.")
                else:
                    # Generate single custom angle
                    if auth_mgr.deduct_credits(user, 1):
                        with st.spinner(f"Generating custom angle..."):
                            custom_prompt = f"{base_prompt}, {custom_angle}, professional photography"
                            
                            assets = build_assets_list(temp_ref_path)
                            payload = {
                                "positive_prompt": custom_prompt,
                                "aspect_ratio": "4:5",
                                "model_type": "nano",
                                "assets": assets
                            }
                            
                            res = generate_image_from_prompt(payload, get_user_out_dir_func("MultiShot"))
                            
                            if res["status"] == "success":
                                st.session_state['multishot_result'] = res['image_path']
                                st.success("✅ Custom angle generated!")
                                st.rerun()
                            else:
                                auth_mgr.add_credits(user, 1)  # Refund
                                st.error(f"Generation failed: {res.get('logs')}")
                    else:
                        st.error("Not enough credits.")
            
            elif multishot_mode == "End Frame Generator":
                if not endframe_description:
                    st.error("Please describe what the end frame should look like.")
                else:
                    if auth_mgr.deduct_credits(user, 1):
                        with st.spinner("🎬 Generating cinematic end frame..."):
                            # Build transition intensity instruction
                            intensity_map = {
                                "Subtle": (
                                    "Make MINIMAL changes from the start frame. "
                                    "Keep the same camera angle, lighting, and composition. "
                                    "Only adjust what the user described — small expression changes, slight movement, minor lighting shifts."
                                ),
                                "Moderate": (
                                    "Allow MODERATE changes from the start frame. "
                                    "The scene can shift noticeably — different pose, adjusted camera angle, evolved lighting — "
                                    "but the overall environment and character identity must remain consistent."
                                ),
                                "Dramatic": (
                                    "Allow DRAMATIC changes from the start frame. "
                                    "The scene can transform significantly — major camera movement, lighting overhaul, "
                                    "new positioning — while preserving character identity and scene continuity."
                                )
                            }
                            intensity_instruction = intensity_map.get(transition_style, intensity_map["Moderate"])
                            
                            # Build the cinematic end frame prompt
                            endframe_prompt = (
                                f"CINEMATIC END FRAME GENERATION\n\n"
                                f"You are a cinematic continuity engine. You are given a START FRAME from a shot. "
                                f"Generate the END FRAME of this same shot.\n\n"
                                f"RULES:\n"
                                f"- Maintain EXACT character identity (face, body, clothing) from the start frame\n"
                                f"- Maintain scene continuity (same location, same world, same time of day unless told otherwise)\n"
                                f"- The end frame should feel like a natural conclusion of the same camera shot\n"
                                f"- {intensity_instruction}\n\n"
                                f"WHAT CHANGES IN THE END FRAME:\n"
                                f"{endframe_description}\n"
                            )
                            if additional_prompt:
                                endframe_prompt += f"\nADDITIONAL CONTEXT: {additional_prompt}\n"
                            
                            endframe_prompt += (
                                f"\nSTYLE: Photorealistic, cinematic, professional cinematography, "
                                f"film grain, shallow depth of field"
                            )
                            
                            assets = build_assets_list(temp_ref_path, label="Reference Character (START FRAME - MAINTAIN CONTINUITY)")
                            selected_ar = endframe_ar
                            payload = {
                                "positive_prompt": endframe_prompt,
                                "aspect_ratio": selected_ar,
                                "model_type": "nano",
                                "assets": assets
                            }
                            
                            res = generate_image_from_prompt(payload, get_user_out_dir_func("MultiShot"))
                            
                            if res["status"] == "success":
                                st.session_state['endframe_result'] = {
                                    "start_frame": temp_ref_path,
                                    "end_frame": res['image_path'],
                                    "description": endframe_description,
                                    "transition": transition_style
                                }
                                st.success("✅ End frame generated!")
                                st.rerun()
                            else:
                                auth_mgr.add_credits(user, 1)  # Refund
                                st.error(f"Generation failed: {res.get('logs')}")
                    else:
                        st.error("Not enough credits.")
    
    # Display Results
    st.divider()
    st.markdown("#### Results")
    
    # End Frame side-by-side display
    if 'endframe_result' in st.session_state:
        ef_data = st.session_state['endframe_result']
        st.markdown(f"**🎬 End Frame** — *{ef_data.get('transition', '')}* transition")
        st.caption(f"Description: {ef_data.get('description', '')}")
        
        col_start, col_end = st.columns(2)
        with col_start:
            st.markdown("**START FRAME**")
            if os.path.exists(ef_data['start_frame']):
                st.image(ef_data['start_frame'], caption="Start Frame", use_container_width=True)
        with col_end:
            st.markdown("**END FRAME**")
            if os.path.exists(ef_data['end_frame']):
                st.image(ef_data['end_frame'], caption="End Frame", use_container_width=True)
                with open(ef_data['end_frame'], "rb") as f:
                    st.download_button(
                        "⬇️ Download End Frame",
                        f,
                        file_name=os.path.basename(ef_data['end_frame']),
                        mime="image/png",
                        key="dl_endframe"
                    )
        st.divider()
    
    # Single result display
    if 'multishot_result' in st.session_state:
        result_path = st.session_state['multishot_result']
        if os.path.exists(result_path):
            st.image(result_path, caption="Generated Multi-Shot", use_container_width=True)
            with open(result_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Result",
                    f,
                    file_name=os.path.basename(result_path),
                    mime="image/png"
                )
    
    # Batch results display
    if 'multishot_batch_results' in st.session_state:
        batch_results = st.session_state['multishot_batch_results']
        if batch_results:
            cols = st.columns(min(3, len(batch_results)))
            for idx, result in enumerate(batch_results):
                with cols[idx % 3]:
                    if os.path.exists(result['path']):
                        st.image(result['path'], caption=result['angle'], use_container_width=True)
                        with open(result['path'], "rb") as f:
                            st.download_button(
                                f"⬇️ {result['angle']}",
                                f,
                                file_name=os.path.basename(result['path']),
                                mime="image/png",
                                key=f"dl_multishot_{idx}"
                            )
