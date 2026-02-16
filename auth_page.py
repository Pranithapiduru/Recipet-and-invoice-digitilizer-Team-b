import streamlit as st  # type: ignore
from config.translations import get_text, get_available_languages  # type: ignore
import hashlib  # type: ignore
import json  # type: ignore
import os  # type: ignore


def apply_auth_css():
    """Apply custom CSS for authentication pages"""
    st.markdown("""
    <style>
        /* Hide default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Auth Container */
        .auth-container {
            max-width: 450px;
            margin: 3rem auto;
            padding: 3rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }
        
        .auth-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .auth-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .auth-subtitle {
            color: #666;
            font-size: 1.1rem;
        }
        
        /* Google Button */
        .google-btn {
            background: white;
            border: 2px solid #ddd;
            padding: 0.8rem 1.5rem;
            border-radius: 10px;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.8rem;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1rem;
            font-weight: 600;
            color: #333;
            margin: 1rem 0;
        }
        
        .google-btn:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
            transform: translateY(-2px);
        }
        
        .google-icon {
            width: 20px;
            height: 20px;
        }
        
        /* Divider */
        .divider {
            display: flex;
            align-items: center;
            text-align: center;
            margin: 1.5rem 0;
            color: #999;
        }
        
        .divider::before,
        .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #ddd;
        }
        
        .divider span {
            padding: 0 1rem;
            font-weight: 600;
        }
        
        /* Form Elements */
        .stTextInput > div > div > input {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            padding: 0.8rem;
            font-size: 1rem;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Buttons */
        .stButton > button {
            border-radius: 10px;
            padding: 0.8rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            width: 100%;
            transition: all 0.3s ease;
        }
        
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
        }
        
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }
        
        /* Links */
        .auth-link {
            text-align: center;
            margin-top: 1.5rem;
            color: #666;
        }
        
        .auth-link a {
            color: #667eea;
            font-weight: 600;
            text-decoration: none;
        }
        
        .auth-link a:hover {
            text-decoration: underline;
        }
        
        /* Language Selector */
        .lang-selector-auth {
            text-align: center;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    """Load users from JSON file"""
    users_file = "data/users.json"
    if os.path.exists(users_file):
        with open(users_file, "r") as f:
            return json.load(f)
    return {}


def save_user(email: str, password: str, name: str = ""):
    """Save new user to JSON file"""
    users_file = "data/users.json"
    os.makedirs("data", exist_ok=True)
    
    users = load_users()
    users[email] = {
        "password": hash_password(password),
        "name": name,
        "auth_method": "email"
    }
    
    with open(users_file, "w") as f:
        json.dump(users, f, indent=2)


def verify_user(email: str, password: str) -> bool:
    """Verify user credentials"""
    users = load_users()
    if email in users:
        return users[email]["password"] == hash_password(password)
    return False


def google_sign_in_placeholder():
    """Placeholder for Google Sign-In (requires OAuth setup)"""
    st.info("""
    🔐 **Google Sign-In Setup Required**
    
    To enable Google authentication:
    1. Create a project in Google Cloud Console
    2. Enable Google+ API
    3. Create OAuth 2.0 credentials
    4. Add credentials to `.env` file
    
    For now, you can use email/password authentication below.
    """)


def render_login_page():
    """Render login page"""
    apply_auth_css()
    
    lang = st.session_state.get("language", "en")
    
    # Back button
    if st.button("← Back to Home"):
        st.session_state["page"] = "landing"
        st.rerun()
    
    st.markdown(f"""
    <div class="auth-container">
        <div class="auth-header">
            <div class="auth-title">🧾 {get_text(lang, 'app_name')}</div>
            <div class="auth-subtitle">{get_text(lang, 'login')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Language selector
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        available_langs = get_available_languages()
        selected_lang = st.selectbox(
            "🌐 Language",
            options=list(available_langs.keys()),
            format_func=lambda x: available_langs[x],
            index=list(available_langs.keys()).index(lang),
            key="lang_selector_login"
        )
        if selected_lang != lang:
            st.session_state["language"] = selected_lang
            st.rerun()
    
    st.markdown("---")
    
    # Google Sign-In Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(f"🔐 {get_text(lang, 'signin_google')}", use_container_width=True):
            google_sign_in_placeholder()
    
    # Divider
    st.markdown(f"""
    <div class="divider">
        <span>{get_text(lang, 'or')}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Email/Password Login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input(
            get_text(lang, "email"),
            placeholder="your.email@example.com",
            key="login_email"
        )
        password = st.text_input(
            get_text(lang, "password"),
            type="password",
            placeholder="••••••••",
            key="login_password"
        )
        
        if st.button(get_text(lang, "login"), type="primary", use_container_width=True):
            if email and password:
                if verify_user(email, password):
                    st.session_state["authenticated"] = True
                    st.session_state["user_email"] = email
                    st.session_state["page"] = "app"
                    st.success(f"✅ {get_text(lang, 'welcome')}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password")
            else:
                st.warning("⚠️ Please fill in all fields")
        
        # Link to signup
        st.markdown(f"""
        <div class="auth-link">
            {get_text(lang, 'no_account')} 
            <a href="#" onclick="return false;">Sign Up</a>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(get_text(lang, "signup"), use_container_width=True):
            st.session_state["page"] = "signup"
            st.rerun()


def render_signup_page():
    """Render signup page"""
    apply_auth_css()
    
    lang = st.session_state.get("language", "en")
    
    # Back button
    if st.button("← Back to Home"):
        st.session_state["page"] = "landing"
        st.rerun()
    
    st.markdown(f"""
    <div class="auth-container">
        <div class="auth-header">
            <div class="auth-title">🧾 {get_text(lang, 'app_name')}</div>
            <div class="auth-subtitle">{get_text(lang, 'signup')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Language selector
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        available_langs = get_available_languages()
        selected_lang = st.selectbox(
            "🌐 Language",
            options=list(available_langs.keys()),
            format_func=lambda x: available_langs[x],
            index=list(available_langs.keys()).index(lang),
            key="lang_selector_signup"
        )
        if selected_lang != lang:
            st.session_state["language"] = selected_lang
            st.rerun()
    
    st.markdown("---")
    
    # Google Sign-In Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(f"🔐 {get_text(lang, 'signin_google')}", use_container_width=True):
            google_sign_in_placeholder()
    
    # Divider
    st.markdown(f"""
    <div class="divider">
        <span>{get_text(lang, 'or')}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Email/Password Signup
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input(
            "Full Name",
            placeholder="John Doe",
            key="signup_name"
        )
        email = st.text_input(
            get_text(lang, "email"),
            placeholder="your.email@example.com",
            key="signup_email"
        )
        password = st.text_input(
            get_text(lang, "password"),
            type="password",
            placeholder="••••••••",
            key="signup_password"
        )
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="••••••••",
            key="signup_confirm_password"
        )
        
        if st.button(get_text(lang, "signup"), type="primary", use_container_width=True):
            if name and email and password and confirm_password:
                if password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    users = load_users()
                    if email in users:
                        st.error("❌ Email already registered")
                    else:
                        save_user(email, password, name)
                        st.success(f"✅ Account created successfully! Please login.")
                        st.session_state["page"] = "login"
                        st.rerun()
            else:
                st.warning("⚠️ Please fill in all fields")
        
        # Link to login
        st.markdown(f"""
        <div class="auth-link">
            {get_text(lang, 'have_account')} 
            <a href="#" onclick="return false;">Login</a>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(get_text(lang, "login"), use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()