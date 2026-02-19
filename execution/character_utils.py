
# Character Creator Utility
# Handles logic to map UI sliders/inputs to valid Prompt Keywords with WEIGHTS

def get_weighted_body_desc(value):
    """0-100 Slider for General Physique"""
    if value < 10: return "(extremely slender frame:1.4), (visible bones:1.2), straight silhouette"
    elif value < 30: return "(slim physique:1.2), petite, slender"
    elif value < 50: return "athletic, fit, toned"
    elif value < 70: return "(curvy figure:1.2), shapely, fit"
    elif value < 90: return "(voluptuous figure:1.3), thick curves, full figure"
    else: return "(heavyset:1.3), (extremely voluptuous:1.5), (massive curves:1.4)"

def get_weighted_muscle_desc(value):
    """0-100 Slider for Muscle Mass"""
    if value < 20: return "soft skin, no visible muscle"
    elif value < 40: return "lightly toned"
    elif value < 60: return "(athletic definition:1.2), visible abs"
    elif value < 80: return "(ripped muscles:1.3), (six pack abs:1.3), muscular arms"
    else: return "(hyper muscular:1.5), (vascularity:1.3), (female bodybuilder:1.4)"

def get_weighted_bust_desc(value, b_type):
    """0-100 Slider + Type for Bust"""
    # Size Base
    size_str = ""
    weight = 1.0
    
    if value < 20: size_str = "flat chest, small bust"; weight=1.0
    elif value < 40: size_str = "average bust"; weight=1.1
    elif value < 60: size_str = "full bust, large breasts"; weight=1.2
    elif value < 80: size_str = "voluptuous bust, heavy cleavage, massive breasts"; weight=1.4
    else: size_str = "huge breasts, hyper huge bust, extreme cleavage"; weight=1.6
    
    # Type Modifier
    type_str = ""
    if b_type == "Augmented / Implants":
        type_str = ", (round implants:1.4), (high profile augmentation:1.3), (fake boobs:1.3), (hard round look:1.2)"
        weight += 0.2 # Augmentation implies prominence
    elif b_type == "Natural / Drop":
        type_str = ", (natural sagging:1.2), (soft teardrop shape:1.2), (heavy natural breasts:1.2)"
    elif b_type == "Perky / Athletic":
        type_str = ", (perky breasts:1.2), (athletic lift:1.1)"
    
    return f"({size_str}:{weight}){type_str}"

def get_weighted_waist_desc(value):
    """0-100 Slider for Waist"""
    if value < 20: return "(extremely cinched waist:1.5), (corset waist:1.4), (wasp waist:1.4)"
    elif value < 40: return "(small waist:1.2), hourglass"
    elif value < 60: return "average waist"
    elif value < 80: return "wide waist, thick midsection"
    else: return "(broad waist:1.3), heavy midsection"

def get_weighted_hip_desc(value):
    """0-100 Slider for Hips"""
    if value < 20: return "narrow hips, straight frame"
    elif value < 40: return "average hips"
    elif value < 60: return "(curvy hips:1.2), shapely"
    elif value < 80: return "(wide hips:1.4), (pear shape:1.3), voluptuous"
    else: return "(extremely wide hips:1.6), (shelf hips:1.5), (hyper exaggerated curves:1.5)"

def get_weighted_glute_desc(value, g_type):
    """0-100 Slider + Type for Glutes"""
    # Size
    size_str = ""
    weight = 1.0
    
    if value < 20: size_str = "flat glutes"; weight=1.0
    elif value < 40: size_str = "average glutes"; weight=1.1
    elif value < 60: size_str = "curvy rear, shapely glutes"; weight=1.2
    elif value < 80: size_str = "large glutes, bubble butt, thick thighs"; weight=1.4
    else: size_str = "massive glutes, hyper exaggerated bubble butt, extreme rear"; weight=1.6

    # Type
    type_str = ""
    if g_type == "BBL / Surgical":
        type_str = ", (surgically enhanced buttocks:1.4), (BBL aesthetic:1.4), (shelf glutes:1.4)"
        weight += 0.2
    elif g_type == "Athletic / Hard":
        type_str = ", (rock hard glutes:1.3), (muscle definition:1.2)"
    elif g_type == "Soft / Natural":
        type_str = ", (soft jiggly glutes:1.2), (natural texture:1.1)"

    return f"({size_str}:{weight}){type_str}"

def get_age_description(value):
    """Maps age number to descriptive text."""
    if value < 25: return f"{value} years old, young adult, fresh face"
    elif value < 35: return f"{value} years old, adult, mature feature"
    elif value < 50: return f"{value} years old, middle aged, mature"
    elif value < 70: return f"{value} years old, senior, elderly"
    else: return f"{value} years old, very elderly, aged"

def get_character_sheet_prompt(base_prompt):
    """Wraps the prompt to generate a reference sheet."""
    # Strong weights for sheet structure + High Fidelity Enforcement
    suffix = "(character reference sheet:1.5), (4 angles:1.5), (front view:1.3), (side view:1.3), (back view:1.3), (three quarter view:1.3), full body, white background, consistent character, detailed anatomy, 8k, (photorealistic:1.4), (raw photo:1.3), (hyperrealistic:1.3), (not illustration:1.5), (not cartoon:1.5), (not 3d render:1.5)"
    return f"{base_prompt}, {suffix}"

def build_character_prompt(attributes):
    """
    Constructs a full character prompt with WEIGHTED attributes.
    """
    
    # Extract Basic
    gender = attributes.get("gender", "Female")
    ethnicity = attributes.get("ethnicity", "Any")
    age_val = attributes.get("age", 25)
    
    # Extract Face
    hair_color = attributes.get("hair_color", "Any")
    hair_style = attributes.get("hair_style", "Any")
    eye_color = attributes.get("eye_color", "Any")
    
    # Granular Makeup
    lashes = attributes.get("lashes", "None")
    eyebrows = attributes.get("eyebrows", "Natural")
    foundation = attributes.get("foundation", "None")
    lipgloss = attributes.get("lipgloss", "None")
    eyeshadow = attributes.get("eyeshadow", "None")
    blush = attributes.get("blush", "None")
    
    # Facial Hair (Enhanced)
    facial_hair = attributes.get("facial_hair", "None")
    facial_hair_color = attributes.get("facial_hair_color", "Same as Hair")
    facial_hair_length = attributes.get("facial_hair_length", "None")
    
    skin_details = attributes.get("skin_details", [])
    
    # Extract Body
    body_val = attributes.get("body_type", 50)
    muscle_val = attributes.get("muscle", 20)
    bust_val = attributes.get("bust", 40)
    bust_type = attributes.get("bust_type", "Natural")
    waist_val = attributes.get("waist", 50)
    hip_val = attributes.get("hips", 50)
    glute_val = attributes.get("glutes", 50)
    glute_type = attributes.get("glute_type", "Natural")
    
    # Extract Tattoos (List)
    tattoo_style = attributes.get("tattoo_style", "None")
    tattoo_places = attributes.get("tattoo_places", []) # List now
    
    # Character Description
    description = attributes.get("description", "")

    # Map Sliders to Weighted Strings
    age_desc = get_age_description(age_val)
    body_desc = get_weighted_body_desc(body_val)
    muscle_desc = get_weighted_muscle_desc(muscle_val)
    waist_desc = get_weighted_waist_desc(waist_val)
    hip_desc = get_weighted_hip_desc(hip_val)
    glute_desc = get_weighted_glute_desc(glute_val, glute_type)
    
    # Contextual Bust
    bust_desc = ""
    # Add female anatomy if gender is female/nb/femme
    is_femme = "Female" in gender or gender == "Non-Binary"
    if is_femme:
        bust_desc = get_weighted_bust_desc(bust_val, bust_type)
        
    # Base Subject
    if ethnicity != "Any":
        subject = f"portrait of a {ethnicity} {gender}"
    else:
        subject = f"portrait of a {gender}"
        
    # Construct Physical Traits List
    traits = [age_desc, body_desc, muscle_desc, waist_desc, hip_desc, glute_desc]
    if bust_desc: traits.append(bust_desc)
    
    # Hair
    h_str = ""
    if hair_color != "Any": h_str += hair_color + " "
    if hair_style != "Any": h_str += hair_style
    if h_str: traits.append(f"{h_str} hair")

    # Eyes & Face
    if eye_color != "Any": traits.append(f"{eye_color} eyes")
    
    # Facial Hair (Enhanced)
    if facial_hair not in ["None", "Clean Shaven"]:
        fh_str = facial_hair
        if facial_hair_length != "None":
            fh_str = f"{facial_hair_length} {facial_hair}"
        if facial_hair_color != "Same as Hair":
            fh_str = f"{facial_hair_color} {fh_str}"
        traits.append(fh_str)
    
    # Makeup (Granular)
    makeup_parts = []
    if lashes != "None": makeup_parts.append(lashes)
    if eyebrows != "Natural": makeup_parts.append(f"{eyebrows} eyebrows")
    if foundation != "None": makeup_parts.append(f"{foundation} foundation")
    if lipgloss != "None": makeup_parts.append(f"{lipgloss} lips")
    if eyeshadow != "None": makeup_parts.append(eyeshadow)
    if blush != "None": makeup_parts.append(blush)
    
    if makeup_parts:
        traits.append(", ".join(makeup_parts))
    
    # Tattoos (Multi-Placement)
    if tattoo_style != "None":
        if tattoo_places:
            joined_places = " AND ".join(tattoo_places) # e.g. "Neck AND Arm"
            traits.append(f"({tattoo_style} tattoos on {joined_places}:1.2)")
        else:
            traits.append(f"{tattoo_style} tattoos")
    
    # Skin
    if skin_details:
        traits.append(", ".join(skin_details))
        
    traits_str = ", ".join(traits)
    
    # Environment & Style (Studio)
    env = "professional studio photography, solid neutral background, seamless backdrop"
    
    # TEXTURE & REALISM BOOST (User Key Requirement)
    # 2026-01-26: Added High Fidelity Skin/Hair Tokens
    texture_boost = "(natural skin texture:1.3), (visible pores:1.2), (subsurface scattering:1.2), (vellus hair:1.1), (detailed iris:1.2), (hyperrealistic hair strands:1.2), 8k, raw photo, fuji film"
    
    lighting = f"soft studio lighting, rembrandt lighting, photography, highly detailed, sharp focus, consistent anatomy, {texture_boost}"
    
    # Outfit (Smart Default)
    outfit = attributes.get("outfit", "")
    if not outfit:
        if is_femme:
            outfit = "(tight black leggings:1.3), (sports bra:1.2), tight fit"
        else:
            outfit = "(athletic shorts:1.2), shirtless, bare chest, athletic fit, no shirt"
    
    # Combine
    full_prompt = f"{subject}, {traits_str}, wearing {outfit}, {env}, {lighting}, full body shot"
    
    # Append Character Description if provided
    if description:
        full_prompt += f", {description}"
    
    # Identity Likeness (from slider)
    likeness = attributes.get("likeness", 50)
    if likeness >= 80:
        full_prompt += (
            ", (identical face to reference:1.5), (exact same person:1.5), "
            "(preserve facial features exactly:1.4), (same bone structure:1.3), "
            "(same nose shape:1.3), (same jawline:1.3), (same eye shape:1.3), "
            "(photographic identity match:1.4), DO NOT alter facial features"
        )
    elif likeness >= 60:
        full_prompt += (
            ", (strong resemblance to reference:1.3), (same face:1.3), "
            "(preserve key facial features:1.2), (similar bone structure:1.2)"
        )
    elif likeness >= 40:
        full_prompt += ", (inspired by reference:1.1), similar features to reference"
    # Below 40: no identity constraints, fully creative
    
    return full_prompt


