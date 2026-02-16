
import streamlit as st  # type: ignore
from config.translations import get_text, get_available_languages  # type: ignore


def apply_landing_css():
    """Apply custom CSS for landing page"""
    st.markdown("""
    <style>
        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Animated Background */
        .main {
            background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }
        
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Hero Section */
        .hero-section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 5rem 3rem;
            border-radius: 30px;
            text-align: center;
            margin: 3rem auto;
            max-width: 1200px;
            box-shadow: 0 30px 90px rgba(0,0,0,0.2);
            border: 2px solid rgba(255,255,255,0.3);
        }
        
        .hero-title {
            font-size: 4.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f5576c 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            animation: fadeInDown 1s ease-out;
            line-height: 1.2;
        }
        
        .hero-subtitle {
            font-size: 1.6rem;
            color: #555;
            margin-bottom: 3rem;
            animation: fadeInUp 1.2s ease-out;
            font-weight: 500;
            line-height: 1.6;
        }
        
        .hero-emoji {
            font-size: 5rem;
            animation: bounce 2s infinite;
            display: inline-block;
            margin-bottom: 1rem;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        
        /* Feature Cards */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2.5rem;
            margin: 4rem auto;
            max-width: 1400px;
        }
        
        .feature-card {
            background: white;
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.12);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border-top: 5px solid transparent;
            position: relative;
            overflow: hidden;
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(90deg, #667eea, #764ba2, #f5576c);
            transform: scaleX(0);
            transition: transform 0.4s ease;
        }
        
        .feature-card:hover::before {
            transform: scaleX(1);
        }
        
        .feature-card:hover {
            transform: translateY(-15px) scale(1.02);
            box-shadow: 0 25px 60px rgba(102, 126, 234, 0.3);
        }
        
        .feature-icon {
            font-size: 4rem;
            margin-bottom: 1.5rem;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .feature-title {
            font-size: 1.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        
        .feature-desc {
            color: #666;
            line-height: 1.8;
            font-size: 1.1rem;
        }
        
        /* Stats Section */
        .stats-container {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.95), rgba(118, 75, 162, 0.95));
            backdrop-filter: blur(10px);
            padding: 4rem 3rem;
            border-radius: 30px;
            margin: 4rem auto;
            max-width: 1200px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            border: 2px solid rgba(255,255,255,0.2);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 3rem;
            margin-top: 2rem;
        }
        
        .stat-item {
            animation: fadeInUp 1s ease-out;
        }
        
        .stat-number {
            font-size: 4rem;
            font-weight: 900;
            color: white;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
            animation: countUp 2s ease-out;
        }
        
        .stat-label {
            font-size: 1.3rem;
            color: rgba(255,255,255,0.95);
            margin-top: 0.5rem;
            font-weight: 600;
        }
        
        /* Animations */
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes countUp {
            from {
                opacity: 0;
                transform: scale(0.5);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        /* Buttons */
        .stButton > button {
            font-size: 1.2rem !important;
            padding: 1rem 3rem !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4) !important;
        }
        
        /* How It Works */
        .how-it-works {
            background: white;
            padding: 4rem 3rem;
            border-radius: 30px;
            margin: 4rem auto;
            max-width: 1200px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }
        
        .step-card {
            text-align: center;
            padding: 2rem;
            transition: transform 0.3s ease;
        }
        
        .step-card:hover {
            transform: scale(1.05);
        }
        
        .step-number {
            font-size: 3rem;
            font-weight: 900;
            background: linear-gradient(135deg, #667eea, #f5576c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Floating elements */
        .float {
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
    </style>
    """, unsafe_allow_html=True)


def render_landing_page():
    """Render the enhanced landing page"""
    apply_landing_css()
    
    # Language selector
    lang = st.session_state.get("language", "en")
    available_langs = get_available_languages()
    
    # Top navigation bar
    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
    with col2:
        selected_lang = st.selectbox(
            "🌐",
            options=list(available_langs.keys()),
            format_func=lambda x: available_langs[x],
            index=list(available_langs.keys()).index(lang),
            key="lang_selector",
            label_visibility="collapsed"
        )
        if selected_lang != lang:
            st.session_state["language"] = selected_lang
            st.rerun()
    
    with col3:
        if st.button("🔐 " + get_text(lang, "login"), use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()
    
    with col4:
        if st.button("✨ " + get_text(lang, "signup"), use_container_width=True, type="primary"):
            st.session_state["page"] = "signup"
            st.rerun()
    
    # Hero Section
    st.markdown(f"""
    <div class="hero-section">
        <div class="hero-emoji float">🧾</div>
        <div class="hero-title">{get_text(lang, "hero_title")}</div>
        <div class="hero-subtitle">{get_text(lang, "hero_subtitle")}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col2:
        if st.button(f"🚀 {get_text(lang, 'get_started')}", use_container_width=True, type="primary", key="cta_start"):
            st.session_state["page"] = "signup"
            st.rerun()
    with col4:
        if st.button(f"📖 {get_text(lang, 'learn_more')}", use_container_width=True, key="cta_learn"):
            st.session_state["show_features"] = True
    
    # Stats Section
    st.markdown(f"""
    <div class="stats-container">
        <h2 style="color: white; font-size: 2.5rem; margin-bottom: 1rem; font-weight: 800;">
            Trusted by Thousands Worldwide
        </h2>
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-number">10K+</div>
                <div class="stat-label">Active Users</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">1M+</div>
                <div class="stat-label">Receipts Scanned</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">99.9%</div>
                <div class="stat-label">AI Accuracy</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">24/7</div>
                <div class="stat-label">Available</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown(f"""
    <div style="text-align: center; margin: 4rem 0 2rem 0;">
        <h2 style="font-size: 3rem; font-weight: 900; background: linear-gradient(135deg, #667eea, #764ba2); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ✨ {get_text(lang, 'features')}
        </h2>
        <p style="font-size: 1.3rem; color: #666; margin-top: 1rem;">
            Everything you need to manage your receipts intelligently
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">{get_text(lang, 'feature_1_title')}</div>
            <div class="feature-desc">{get_text(lang, 'feature_1_desc')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">{get_text(lang, 'feature_2_title')}</div>
            <div class="feature-desc">{get_text(lang, 'feature_2_desc')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">🌐</div>
            <div class="feature-title">{get_text(lang, 'feature_3_title')}</div>
            <div class="feature-desc">{get_text(lang, 'feature_3_desc')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <div class="feature-title">{get_text(lang, 'feature_4_title')}</div>
            <div class="feature-desc">{get_text(lang, 'feature_4_desc')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # How it works
    st.markdown("""
    <div class="how-it-works">
        <h2 style="text-align: center; font-size: 3rem; font-weight: 900; 
                   background: linear-gradient(135deg, #667eea, #764ba2); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 3rem;">
            🎯 How It Works
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">1️⃣</div>
            <h3 style="color: #667eea; font-size: 1.8rem; margin: 1rem 0;">Upload</h3>
            <p style="color: #666; font-size: 1.1rem; line-height: 1.6;">
                Simply upload your receipt images or PDFs with drag & drop
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">2️⃣</div>
            <h3 style="color: #764ba2; font-size: 1.8rem; margin: 1rem 0;">Extract</h3>
            <p style="color: #666; font-size: 1.1rem; line-height: 1.6;">
                AI automatically extracts all important data in seconds
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">3️⃣</div>
            <h3 style="color: #f5576c; font-size: 1.8rem; margin: 1rem 0;">Analyze</h3>
            <p style="color: #666; font-size: 1.1rem; line-height: 1.6;">
                Get powerful insights and track your spending patterns
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Final CTA
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(f"🎉 {get_text(lang, 'get_started')} - It's Free!", use_container_width=True, type="primary", key="final_cta"):
            st.session_state["page"] = "signup"
            st.rerun()
