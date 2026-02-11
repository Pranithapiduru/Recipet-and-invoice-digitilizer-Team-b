import streamlit as st  # type: ignore
from database.db import init_db  # type: ignore
from ui.landing_page import render_landing_page  # type: ignore
from ui.auth_page import render_login_page, render_signup_page
from ui.sidebar import render_sidebar
from ui.upload_ui import render_upload_ui
from ui.dashboard_ui import render_dashboard
from ui.validation_ui import validation_ui
from ui.analytics_ui import render_analytics
from ui.styles import apply_global_styles
from config.translations import get_text

# ================= CONFIG =================
st.set_page_config(
    page_title="Receipt Vault Analyzer",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="auto"
)

# ================= INIT =================
if "init_done" not in st.session_state:
    init_db()
    st.session_state["init_done"] = True

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state["page"] = "landing"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "language" not in st.session_state:
    st.session_state["language"] = "en"

# ================= ROUTING =================
def main():
    """Main application router"""
    
    # Check authentication status
    if not st.session_state.get("authenticated", False):
        # Show landing/auth pages
        page = st.session_state.get("page", "landing")
        
        if page == "landing":
            render_landing_page()
        elif page == "login":
            render_login_page()
        elif page == "signup":
            render_signup_page()
    else:
        # User is authenticated - show main app with professional styling
        apply_global_styles()
        render_main_app()


def render_main_app():
    """Render the main application after authentication"""
    lang = st.session_state.get("language", "en")
    
    # Render sidebar and get selected page
    app_page = render_sidebar()
    
    # Render selected page
    if app_page == get_text(lang, "upload_receipt") or app_page == "Upload Receipt":
        render_upload_ui()
    elif app_page == get_text(lang, "validation") or app_page == "Validation":
        validation_ui()
    elif app_page == get_text(lang, "dashboard") or app_page == "Dashboard":
        render_dashboard()
    elif app_page == get_text(lang, "analytics") or app_page == "Analytics":
        render_analytics()
    elif app_page == get_text(lang, "chat") or app_page == "Chat with Data":
        from ui.chat_ui import render_chat
        render_chat()


if __name__ == "__main__":
    main()
