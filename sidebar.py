import streamlit as st  # type: ignore
from database.queries import clear_all_receipts  # type: ignore
from config.translations import get_text, get_available_languages  # type: ignore


def render_sidebar():
    """Render sidebar with navigation and settings"""
    lang = st.session_state.get("language", "en")
    
    with st.sidebar:
        # App branding
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem 0; border-bottom: 3px solid #667eea;">
            <h1 style="font-size: 2.5rem; margin: 0;">🧾</h1>
            <h3 style="margin: 0.5rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;">
                {get_text(lang, 'app_name')}
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # User info
        user_email = st.session_state.get("user_email", "User")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.2rem; border-radius: 12px; color: white; text-align: center; 
                    margin: 1rem 0; box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);">
            <div style="font-size: 0.9rem; opacity: 0.95;">👤 {get_text(lang, 'welcome')}</div>
            <div style="font-weight: 700; margin-top: 0.4rem; font-size: 1.05rem;">{user_email}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Language Selector
        st.markdown(f"### 🌐 {get_text(lang, 'language')}")
        available_langs = get_available_languages()
        selected_lang = st.selectbox(
            "Select Language",
            options=list(available_langs.keys()),
            format_func=lambda x: available_langs[x],
            index=list(available_langs.keys()).index(lang),
            key="sidebar_lang_selector",
            label_visibility="collapsed"
        )
        if selected_lang != lang:
            st.session_state["language"] = selected_lang
            st.rerun()
        
        st.divider()
        
        # API KEY INPUT
        api_key = st.text_input(
            "🔑 Gemini API Key",
            type="password",
            help="Enter your Google Gemini API Key for AI features",
            key="gemini_api_key_input"
        )
        
        if api_key:
            st.session_state["GEMINI_API_KEY"] = api_key
            st.success("✅ API Key set!")
        else:
            st.info("ℹ️ Enter API Key for AI features")

        st.divider()

        # NAVIGATION
        st.markdown(f"### 📍 {get_text(lang, 'features')}")
        
        # Create navigation options with translations
        nav_options = [
            get_text(lang, "upload_receipt"),
            get_text(lang, "validation"),
            get_text(lang, "dashboard"),
            get_text(lang, "analytics"),
            get_text(lang, "chat"),
            get_text(lang, "erp_integration")
        ]
        
        page = st.radio(
            "Navigate to",
            nav_options,
            index=0,
            label_visibility="collapsed"
        )

        st.divider()

        # SETTINGS
        with st.expander(f"⚙️ {get_text(lang, 'settings')}"):
            if st.button("🗑 Clear All Data", type="secondary", use_container_width=True):
                if st.session_state.get("confirm_delete", False):
                    clear_all_receipts()
                    st.toast("All receipts deleted!", icon="🗑")
                    st.session_state["confirm_delete"] = False
                    st.rerun()
                else:
                    st.session_state["confirm_delete"] = True
                    st.warning("⚠️ Click again to confirm deletion")
            
            st.divider()
            
            # Logout button
            if st.button(f"🚪 {get_text(lang, 'logout')}", type="primary", use_container_width=True):
                st.session_state["authenticated"] = False
                st.session_state["user_email"] = None
                st.session_state["page"] = "landing"
                st.success("✅ Logged out successfully!")
                st.rerun()

        st.divider()
        
        # BUDGET LIMIT TRACKER
        st.markdown("### 💰 Monthly Budget")
        
        # Get current month spending
        from database.queries import fetch_all_receipts
        from datetime import datetime
        import pandas as pd
        
        receipts = fetch_all_receipts()
        current_month = datetime.now().strftime("%Y-%m")
        
        if receipts:
            df = pd.DataFrame(receipts)
            df["date"] = pd.to_datetime(df["date"])
            current_month_df = df[df["date"].dt.strftime("%Y-%m") == current_month]
            current_spend = current_month_df["amount"].sum()
        else:
            current_spend = 0
        
        # Budget input
        budget_limit = st.number_input(
            "Set Monthly Limit (₹)",
            min_value=0.0,
            value=st.session_state.get("monthly_budget", 50000.0),
            step=1000.0,
            key="sidebar_budget_input"
        )
        st.session_state["monthly_budget"] = budget_limit
        
        # Calculate percentage
        if budget_limit > 0:
            percent_used = (current_spend / budget_limit) * 100
        else:
            percent_used = 0
        
        # Progress bar with color coding
        if percent_used < 70:
            progress_color = "🟢"
            status_text = "On Track"
        elif percent_used < 90:
            progress_color = "🟡"
            status_text = "Warning"
        else:
            progress_color = "🔴"
            status_text = "Over Budget"
        
        # Display progress
        st.progress(min(percent_used / 100, 1.0), text=f"{percent_used:.1f}% Used")
        
        # Budget summary card
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                    padding: 1rem; border-radius: 10px; color: white; margin-top: 0.5rem;" class="sidebar-white-text">
            <div style="font-size: 0.85rem; opacity: 0.9;" class="sidebar-white-text">💸 Spent This Month</div>
            <div style="font-size: 1.5rem; font-weight: 700;" class="sidebar-white-text">₹{current_spend:,.0f}</div>
            <div style="font-size: 0.85rem; margin-top: 0.3rem;" class="sidebar-white-text">of ₹{budget_limit:,.0f}</div>
            <div style="font-size: 0.9rem; margin-top: 0.5rem; font-weight: 600;" class="sidebar-white-text">{progress_color} {status_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Remaining budget
        remaining = budget_limit - current_spend
        if remaining > 0:
            st.success(f"✅ ₹{remaining:,.0f} remaining")
        else:
            st.error(f"⚠️ ₹{abs(remaining):,.0f} over budget!")

        st.markdown("---")
        st.caption("v2.0 • Built with ❤️ using Streamlit & Gemini AI")
        
        return page