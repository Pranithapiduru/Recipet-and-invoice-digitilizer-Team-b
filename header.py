import streamlit as st  # type: ignore
from config.translations import get_text  # type: ignore

def render_header():
    """Render a simple, clean header with navigation"""
    user_email = st.session_state.get("user_email", "User")
    lang = st.session_state.get("language", "en")
    
    # Simple CSS for header layout - No fancy glass effects
    st.markdown("""
    <style>
        .header-container {
            padding: 1rem 0;
            margin-bottom: 2rem;
            border-bottom: 1px solid #e2e8f0;
        }
        .logo-title {
            font-size: 1.5rem;
            color: #1e293b;
            font-weight: 700;
            margin: 0;
        }
        .logo-subtitle {
            font-size: 0.9rem;
            color: #64748b;
            margin: 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header Container
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    
    # 2-Column Layout: Logo and User
    c1, c2 = st.columns([3, 1])
    
    with c1:
        st.markdown("""
        <div>
            <span style="font-size: 1.5rem;">🧾</span>
            <span class="logo-title">Receipt Vault Digitizer</span>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        # Simple User Display
        st.caption(f"Signed in as: {user_email}")
        if st.button("Sign Out", key="logout_btn", type="secondary"):
            st.session_state.clear()
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

    # Navigation Buttons (Standard Streamlit Buttons)
    nav_options = [
        ("📤 Upload", "upload"),
        ("✅ Validation", "validation"),
        ("📊 Dashboard", "dashboard"),
        ("📈 Analytics", "analytics"),
        ("💬 Chat", "chat")
    ]
    
    # Get current page
    if "current_nav_page" not in st.session_state:
        # Default to Dashboard if requested "1st dash board"
        st.session_state["current_nav_page"] = "dashboard"
    
    # Render Navigation Row
    cols = st.columns(len(nav_options))
    for idx, (label, page_key) in enumerate(nav_options):
        with cols[idx]:
            # Use Primary style for active page
            btn_type = "primary" if st.session_state.get("current_nav_page") == page_key else "secondary"
            if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=btn_type):
                st.session_state["current_nav_page"] = page_key
                st.rerun()
                
    st.divider()
    
    return st.session_state.get("current_nav_page", "dashboard")
