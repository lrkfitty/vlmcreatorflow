import streamlit as st

def inject_magic_css():
    """Injects the global CSS for Aurora Background and Magic UI primitives."""
    css = """
    <style>
        /* --- GLOBAL RESET & TYPOGRAPHY --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');
        
        :root {
            --bg-color: #000000; /* Pure Black */
            --text-color: #FFFFFF; /* Pure White */
            --card-bg: rgba(255, 255, 255, 0.05);
            --border-color: rgba(255, 255, 255, 0.15); /* Stronger Border */
            --primary-glow: conic-gradient(from 180deg at 50% 50%, #2a8af6 0deg, #a853ba 180deg, #e92a67 360deg);
        }
        
        html, body {
            font-family: 'Inter', sans-serif;
            color: var(--text-color) !important;
        }
        
        /* Force background to black for main container */
        .stApp {
            background-color: var(--bg-color) !important;
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(76, 29, 149, 0.15), transparent 25%), 
                radial-gradient(circle at 85% 30%, rgba(14, 165, 233, 0.15), transparent 25%);
            background-attachment: fixed;
        }

        /* --- TEXT READABILITY --- */
        h1, h2, h3, h4, h5, h6, label, .stMarkdown p, .stCaption {
            color: #FFFFFF !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.5); /* separation from bg */
        }
        
        .stCaption {
            color: #A3A3A3 !important; /* Slightly dimmer for hierarchy */
        }

        /* --- GLASSMOPHISM CARD (The "Aura") --- */
        /* We target the container directly if possible, or use our wrapper */
        .glass-card {
            background: rgba(20, 20, 20, 0.6); /* Darker base */
            backdrop-filter: blur(24px) saturate(180%);
            -webkit-backdrop-filter: blur(24px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 
                0 4px 6px -1px rgba(0, 0, 0, 0.1), 
                0 2px 4px -1px rgba(0, 0, 0, 0.06),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
        }
        
        .glass-card:hover {
            border-color: rgba(255, 255, 255, 0.3);
            box-shadow: 
                0 20px 25px -5px rgba(0, 0, 0, 0.2), 
                0 10px 10px -5px rgba(0, 0, 0, 0.1),
                0 0 15px rgba(56, 189, 248, 0.2); /* Blue Glow */
            transform: translateY(-2px);
        }

        /* --- MAGIC TEXT (Aurora Gradient) --- */
        @keyframes aurora-text {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .magic-text {
            background: linear-gradient(
                90deg, 
                #FFFFFF 0%, 
                #38BDF8 25%, 
                #C084FC 50%, 
                #F472B6 75%, 
                #FFFFFF 100%
            );
            background-size: 200% auto;
            color: transparent !important;
            -webkit-text-fill-color: transparent !important;
            -webkit-background-clip: text;
            background-clip: text;
            font-weight: 900;
            letter-spacing: -0.03em;
            animation: aurora-text 6s linear infinite;
        }
        
        /* --- SHINY BUTTONS (Aggressive Override) --- */
        div.stButton > button {
             background: linear-gradient(110deg, #1e293b 0%, #334155 25%, #475569 50%, #334155 75%, #1e293b 100%);
             background-size: 200% 200%;
             color: #FFF !important;
             border: 1px solid rgba(255,255,255,0.2) !important;
             border-radius: 8px !important;
             font-weight: 600 !important;
             transition: all 0.3s ease !important;
             animation: shine 4s linear infinite;
             box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
        }
        div.stButton > button:hover {
             color: #FFFFFF !important;
             border-color: #60A5FA !important; /* Blue highlight */
             transform: translateY(-2px);
             box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05), 0 0 20px rgba(96, 165, 250, 0.5); /* Blue Glow */
        }
        
        div.stButton > button[kind="primary"] {
             background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%) !important;
             border: none !important;
             box-shadow: 0 0 15px rgba(124, 58, 237, 0.4);
        }

        /* --- GRID & HOVER IMAGES --- */
        [data-testid="stImage"] img {
             border-radius: 12px;
             transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), filter 0.3s ease;
             border: 1px solid rgba(255,255,255,0.1);
        }
        
        [data-testid="stImage"]:hover img {
             transform: scale(1.05);
             filter: brightness(1.1);
             border-color: rgba(255,255,255,0.5);
             box-shadow: 0 10px 40px -10px rgba(0,0,0,0.5);
             z-index: 10;
        }

        /* --- INPUT FIELDS (Seamless) --- */
        .stTextInput input, 
        .stSelectbox div[data-baseweb="select"] > div,
        .stMultiSelect div[data-baseweb="select"] > div,
        .stTextArea textarea {
            background-color: #0F172A !important; /* Opaque Dark Slate */
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            color: #FFFFFF !important;
            caret-color: #38BDF8; /* Cyan Cursor */
            border-radius: 8px !important;
        }
        
        .stTextInput input:focus,
        .stTextArea textarea:focus {
            border-color: #38BDF8 !important; /* Cyan Focus */
            background-color: #1E293B !important; /* Slightly lighter opaque */
            box-shadow: 0 0 0 1px #38BDF8;
        }
        
        /* Sidebar Glass */
        [data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.7) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255,255,255,0.1);
        }
        
        /* --- DROPDOWNS & MENUS (NUCLEAR OPTION) --- */
        /* Force EVERYTHING inside the dropdown menu to be Black Bg / White Text */
        
        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        ul[data-baseweb="menu"] {
             background-color: #000000 !important;
             color: #FFFFFF !important;
             border: 1px solid #333 !important;
        }

        li[data-baseweb="option"] {
             background-color: #000000 !important;
             color: #E0E0E0 !important; /* Slightly off-white for contrast */
        }
        
        li[data-baseweb="option"] * {
             color: #E0E0E0 !important;
        }

        li[data-baseweb="option"]:hover,
        li[data-baseweb="option"][aria-selected="true"] {
             background-color: #222222 !important;
             color: #FFFFFF !important;
        }
        
        li[data-baseweb="option"]:hover *,
        li[data-baseweb="option"][aria-selected="true"] * {
             color: #FFFFFF !important;
        }

        /* The container box */
        .stSelectbox div[data-baseweb="select"] > div {
             background-color: #000000 !important;
             color: #FFFFFF !important;
             border: 1px solid #444 !important;
        }
        
        .stSelectbox div[data-baseweb="select"] > div * {
             color: #FFFFFF !important;
        }

        
        /* --- CIRCULAR PROGRESS --- */
        @keyframes spin {
             0% { transform: rotate(0deg); }
             100% { transform: rotate(360deg); }
        }
        
        .circular-loader {
             width: 48px;
             height: 48px;
             border-radius: 50%;
             background: conic-gradient(#FFFFFF 0%, transparent 40%);
             position: relative;
             animation: spin 1s linear infinite;
        }
        .circular-loader::before {
             content: "";
             position: absolute;
             inset: 4px;
             background: #000;
             border-radius: 50%;
        }
        
        /* --- HOVER DOWNLOAD BUTTON --- */
        .hover-btn-wrap {
            position: relative;
            display: inline-block;
            overflow: hidden;
            border-radius: 8px;
            cursor: pointer;
        }
        
        .hover-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            background: #111;
            color: #FFF;
            border: 1px solid #333;
            padding: 8px 16px;
            font-weight: 500;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .hover-btn-wrap:hover .hover-btn {
             background: #FFF;
             color: #000;
             transform: translateY(-100%);
        }
        
        .hover-btn-reveal {
             position: absolute;
             inset: 0;
             display: flex;
             align-items: center;
             justify-content: center;
             background: #FFF;
             color: #000;
             transform: translateY(100%);
             transition: all 0.3s ease;
        }
        
        .hover-btn-wrap:hover .hover-btn-reveal {
             transform: translateY(0);
        }

        /* --- TABS --- */
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1.2rem !important; /* Bigger */
            font-weight: 700 !important; /* Bold */
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Active Tab Highlight */
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
             color: #FFFFFF !important;
             border-bottom-color: #38BDF8 !important;
        }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def magic_text(text, type="h1"):
    """Renders text with the Aurora Gradient animation."""
    st.markdown(f"<{type} class='magic-text'>{text}</{type}>", unsafe_allow_html=True)

def card_begin():
    """Starts a Glassmorphism Card Wrapper."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)

def circular_progress():
    st.markdown('<div class="circular-loader"></div>', unsafe_allow_html=True)

def hover_button(label="Download", key=None):
    """(Visual Only) Renders the CSS for the hover button. 
       For actual functionality, we still need st.button or st.download_button overlaid or handled via callbacks.
       Since Streamlit doesn't allow custom HTML to trigger Python callbacks easily, 
       we will use this for visual flair on links or static actions, 
       or wrap a transparent download button on top if possible (tricky).
       
       For now, returning HTML string."""
    return f"""
    <div class="hover-btn-wrap">
        <div class="hover-btn">{label}</div>
        <div class="hover-btn-reveal">⬇</div>
    </div>
    """
