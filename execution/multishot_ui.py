"""
Multi-Shot Character Reference Generator

Generates multiple angles of a character from a single reference image.
"""

import streamlit as st
from execution.character_utils import get_character_sheet_prompt
from execution.generate_image import generate_image_from_prompt
from execution.auth import auth_mgr
import os

def render_multishot_ui(get_user_out_dir_func):
    """
    Renders the Multi-Shot reference generator UI.
    
    Args:
        get_user_out_dir_func: Function to get user output directory
    """
    st.markdown("### Multi-Shot Reference Generator")
    st.info("Upload a character reference and generate multiple angles for consistency across your content.")
    
    with st.form("multishot_form"):
        # Reference Image Upload
        st.markdown("**1. Upload Reference Image**")
        ref_upload = st.file_uploader(
            "Character or Object Reference", 
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear reference image of your character or object"
        )
        
        if ref_upload:
            st.image(ref_upload, caption="Reference Preview", use_container_width=True)
        
        st.divider()
        
        # Generation Mode
        st.markdown("**2. Output Format**")
        multishot_mode = st.selectbox(
            "Generation Mode",
            [
                "Character Sheet (4 Angles)", 
                "Individual Shots (Batch)", 
                "Single Custom Angle"
            ]
        )
        
        # Angle Selection (for Individual Shots)
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
        
        st.divider()
        
        # Additional prompts
        st.markdown("**3. Additional Details (Optional)**")
        additional_prompt = st.text_area(
            "Additional Context",
            placeholder="e.g. wearing black jacket, cyberpunk aesthetic, neon lighting",
            height=80,
            help="Add specific details you want to maintain across all angles"
        )
        
        st.divider()
        
        # Queue or Generate
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
            
            # Handle different modes
            if multishot_mode == "Character Sheet (4 Angles)":
                # Generate 4-angle character sheet
                full_prompt = get_character_sheet_prompt(base_prompt)
                
                # Credit check
                if auth_mgr.deduct_credits(user, 1):
                    with st.spinner("Generating 4-angle character sheet..."):
                        assets = [{"path": temp_ref_path, "label": "Reference Character"}]
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
                                
                                assets = [{"path": temp_ref_path, "label": "Reference Character"}]
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
                            
                            assets = [{"path": temp_ref_path, "label": "Reference Character"}]
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
    
    # Display Results
    st.divider()
    st.markdown("#### Results")
    
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
