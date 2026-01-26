import streamlit as st

def inject_magic_css():
    """Injects the global CSS for Aurora Background and Magic UI primitives."""
    css = """
    <style>
        /* --- GLOBAL THEME & AURORA --- */
        :root {
            --bg-color: #0A0A0A;
            --card-bg: rgba(255, 255, 255, 0.03);
            --border-color: rgba(255, 255, 255, 0.1);
            --primary-glow: conic-gradient(from 180deg at 50% 50%, #2a8af6 0deg, #a853ba 180deg, #e92a67 360deg);
        }
        
        .stApp {
            background-color: var(--bg-color) !important;
            background-image: 
                radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.1) 0px, transparent 50%), 
                radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.1) 0px, transparent 50%);
            color: #E2E8F0 !important;
        }
        
        /* Aurora Text Animation */
        @keyframes aurora-text {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .magic-text {
            background: linear-gradient(
                to right, 
                #62cff4, 
                #2c67f2, 
                #62cff4
            );
            background-size: 200% auto;
            color: transparent;
            -webkit-background-clip: text;
            background-clip: text;
            animation: aurora-text 3s linear infinite;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        /* --- GLASSMOPHISM CARD --- */
        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .glass-card:hover {
            border-color: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
        }
        
        /* --- SHINY BUTTON --- */
        .shiny-button {
            background: linear-gradient(110deg, #171717 45%, #333 50%, #171717 55%);
            background-size: 200% 100%;
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
            animation: shine 3s linear infinite;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-decoration: none !important;
            transition: 0.2s;
        }
        @keyframes shine {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        .shiny-button:hover {
            border-color: #fff;
            box-shadow: 0 0 20px rgba(255,255,255,0.1);
        }

        /* --- NEON GRADIENT BORDER --- */
        .neon-border {
            position: relative;
            background: #111;
            border-radius: 12px;
            z-index: 1;
        }
        .neon-border::before {
            content: "";
            position: absolute;
            inset: -1px;
            z-index: -1;
            background: var(--primary-glow);
            border-radius: 13px;
            opacity: 0.5;
            filter: blur(8px);
        }

        /* --- CUSTOM SCROLLBAR --- */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0A0A0A; 
        }
        ::-webkit-scrollbar-thumb {
            background: #333; 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555; 
        }
        
        /* --- STREAMLIT OVERRIDES --- */
        [data-testid="stSidebar"] {
            background-color: rgba(10, 10, 10, 0.8) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--border-color);
        }
        
        .stButton button {
            background: #171717;
            color: #e5e5e5;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        h1, h2, h3 {
             font-family: 'Inter', sans-serif !important;
             color: #FFFFFF !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def magic_text(text, type="h1"):
    """Renders text with the Aurora Gradient animation."""
    st.markdown(f"<{type} class='magic-text'>{text}</{type}>", unsafe_allow_html=True)

def card_begin():
    """Starts a Glassmorphism Card Wrapper. Must check st.container inside?"""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)
