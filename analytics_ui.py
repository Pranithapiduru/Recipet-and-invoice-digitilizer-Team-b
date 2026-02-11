import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore
from datetime import datetime, timedelta  # type: ignore
from database.queries import fetch_all_receipts  # type: ignore
from config.translations import get_text, TRANSLATIONS  # type: ignore
from config.config import CURRENCY_SYMBOL  # type: ignore
from ai.insights import generate_ai_insights  # type: ignore
from analytics.forecasting import (  # type: ignore
    calculate_moving_averages,
    predict_next_month_spending,
    predict_spending_polynomial
)
from analytics.advanced_analytics import (  # type: ignore
    detect_subscriptions,
    calculate_burn_rate
)


def apply_custom_css():
    """Apply custom CSS for enhanced UI"""
    st.markdown("""
    <style>
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Summary cards */
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            margin: 1rem 0;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            border-left: 5px solid #ffd700;
        }
        
        .summary-card-green {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            margin: 1rem 0;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            border-left: 5px solid #ffd700;
        }
        
        .summary-card-orange {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            margin: 1rem 0;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            border-left: 5px solid #ffd700;
        }
        
        .summary-card-blue {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            margin: 1rem 0;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            border-left: 5px solid #ffd700;
        }
        
        /* Insight highlights */
        .insight-highlight {
            background: rgba(255, 255, 255, 0.2);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            font-size: 1.05rem;
            backdrop-filter: blur(10px);
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: #f0f2f6;
            border-radius: 10px 10px 0 0;
            padding: 0 24px;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        /* KPI cards */
        div[data-testid="metric-container"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        div[data-testid="metric-container"] label {
            color: white !important;
        }
        
        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: white !important;
        }
        
        div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
            color: #ffd700 !important;
        }
    </style>
    """, unsafe_allow_html=True)


def render_analytics():
    apply_custom_css()
    lang = st.session_state.get("language", "en")
    st.markdown(get_text(lang, "analytics_header"))
    st.markdown(get_text(lang, "analytics_subtitle"))
    st.divider()

    # ---------------- Fetch Data ----------------
    receipts = fetch_all_receipts()

    if not receipts:
        st.info(get_text(lang, "no_receipts_analytics"))
        return

    df = pd.DataFrame(receipts)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")

    # ---------------- Sidebar Filters ----------------
    st.sidebar.markdown(get_text(lang, "analytics_filters_header"))
    st.sidebar.divider()

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    date_range = st.sidebar.date_input(
        get_text(lang, "select_date_range"),
        value=(df['date'].min(), df['date'].max()),
        min_value=df['date'].min(),
        max_value=df['date'].max()
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
        df_filtered = df.loc[mask]
    else:
        df_filtered = df.copy()

    # ---------------- Budget Tracker ----------------
    st.sidebar.divider()
    st.sidebar.markdown(get_text(lang, "monthly_budget_label"))

    budget_goal = st.sidebar.number_input(
        get_text(lang, "set_monthly_limit"),
        min_value=0.0,
        value=st.session_state.get("monthly_budget", 50000.0),
        step=1000.0
    )
    st.session_state["monthly_budget"] = budget_goal

    current_month = datetime.now().strftime("%Y-%m")
    current_month_df = df[df["date"].dt.strftime("%Y-%m") == current_month]
    current_month_total = current_month_df["amount"].sum()
    days_passed = datetime.now().day

    budget_stats = calculate_burn_rate(current_month_total, budget_goal, days_passed)

    if budget_stats:
        st.sidebar.progress(
            budget_stats["percent_used"] / 100,
            text=f"{budget_stats['percent_used']:.1f}% {get_text(lang, 'used_label')}"
        )
        st.sidebar.caption(
            get_text(lang, "spent_of_label").format(spent=current_month_total, budget=budget_goal)
        )
        status_text = get_text(lang, "status_over_budget") if budget_stats["projected"] > budget_goal else get_text(lang, "status_within_budget")
        st.sidebar.markdown(f"**{get_text(lang, 'status_label')}:** {status_text}")
        if budget_stats["projected"] > budget_goal:
            st.sidebar.warning(
                f"📉 {get_text(lang, 'projected_label')}: {CURRENCY_SYMBOL}{budget_stats['projected']:,.0f}"
            )

    # ---------------- Export ----------------
    st.sidebar.divider()
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        label=get_text(lang, "download_analytics_btn"),
        data=csv,
        file_name="receipt_analytics.csv",
        mime="text/csv",
        use_container_width=True
    )

    # ---------------- KPIs ----------------
    st.markdown(get_text(lang, "kpi_header"))

    col1, col2, col3, col4 = st.columns(4)

    total_spending = df_filtered["amount"].sum()
    avg_transaction = df_filtered["amount"].mean() if not df_filtered.empty else 0
    transaction_count = len(df_filtered)

    if not df_filtered.empty:
        cat_group = df_filtered.groupby("category")["amount"].sum().sort_values(ascending=False)
        top_cat = cat_group.index[0]
        top_cat_amt = cat_group.iloc[0]
    else:
        top_cat, top_cat_amt = "N/A", 0

    col1.metric(get_text(lang, "total_spending"), f"{CURRENCY_SYMBOL}{total_spending:,.2f}")
    col2.metric(get_text(lang, "avg_transaction"), f"{CURRENCY_SYMBOL}{avg_transaction:,.2f}")
    col3.metric(get_text(lang, "receipts_scanned"), f"{transaction_count:,}")
    col4.metric(get_text(lang, "top_category"), top_cat, f"{CURRENCY_SYMBOL}{top_cat_amt:,.2f}")

    st.divider()

    # ---------------- Tabs ----------------
    tab_trends, tab_cats, tab_vendors, tab_advanced, tab_ai = st.tabs([
        get_text(lang, "trends_tab"),
        get_text(lang, "categories_tab"),
        get_text(lang, "vendors_tab"),
        get_text(lang, "advanced_tab"),
        get_text(lang, "ai_tab")
    ])

    # ================== TRENDS TAB ==================
    with tab_trends:
        st.markdown(get_text(lang, "monthly_spending_trend_header"))
        
        monthly_df = (
            df_filtered.set_index("date")
            .resample("M")["amount"]
            .sum()
            .reset_index()
        )
        monthly_df.columns = ['Month', 'amount_inr'] # Rename columns for clarity and localization

        fig_monthly = px.line(
            monthly_df,
            x="Month",
            y="amount_inr",
            title=get_text(lang, "monthly_trend_title"),
            labels={"Month": get_text(lang, "date"), "amount_inr": get_text(lang, "amount_inr")},
            markers=True
        )
        
        fig_monthly.update_traces(
            line=dict(color='#667eea', width=3),
            marker=dict(size=10, color='#764ba2')
        )
        
        fig_monthly.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            hovermode='x unified',
            xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
        )

        poly_forecast = predict_spending_polynomial(df, degree=2)
        if poly_forecast is not None:
            fig_monthly.add_trace(go.Scatter(
                x=poly_forecast["date"],
                y=poly_forecast["predicted_amount"],
                mode="lines",
                name=get_text(lang, "ai_trend_prediction"),
                line=dict(dash="dash", color="#f5576c", width=2)
            ))

        st.plotly_chart(fig_monthly, use_container_width=True)
        
        avg_month = 0.0
        # SUMMARY BELOW GRAPH
        if not monthly_df.empty:
            st.markdown(get_text(lang, "monthly_trend_summary"))
            tcol1, tcol2, tcol3, tcol4 = st.columns(4)
            
            max_month = monthly_df.loc[monthly_df['amount_inr'].idxmax()]
            min_month = monthly_df.loc[monthly_df['amount_inr'].idxmin()]
            avg_month = monthly_df['amount_inr'].mean()
            variance = monthly_df['amount_inr'].std()
            
            tcol1.metric(get_text(lang, "highest_spending_month"), max_month['Month'].strftime('%B %Y'))
            tcol2.metric(get_text(lang, "lowest_spending_month"), min_month['Month'].strftime('%B %Y'))
            tcol3.metric(get_text(lang, "avg_monthly_spending"), f"₹{avg_month:,.0f}")
            tcol4.metric(get_text(lang, "variance_label"), f"₹{variance:,.0f}")

        st.divider()
        st.markdown(get_text(lang, "daily_spending_ma_header"))
        
        daily_spend, ma_7 = calculate_moving_averages(df_filtered, 7)
        daily_df = daily_spend.reset_index() # For easier access to date and amount

        fig_ma = go.Figure()
        fig_ma.add_trace(go.Scatter(
            x=daily_spend.index, 
            y=daily_spend, 
            name=get_text(lang, "daily_spending"),
            line=dict(color='rgba(102, 126, 234, 0.4)', width=1),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        fig_ma.add_trace(go.Scatter(
            x=ma_7.index, 
            y=ma_7, 
            name=get_text(lang, "seven_day_average"),
            line=dict(color='#f5576c', width=3)
        ))
        
        fig_ma.update_layout(
            title=get_text(lang, "daily_spending_pattern_title"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified',
            xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
        )
        
        st.plotly_chart(fig_ma, use_container_width=True)
        
        # SUMMARY BELOW GRAPH
        if not daily_spend.empty:
            st.markdown(get_text(lang, "daily_spending_summary"))
            dcol1, dcol2, dcol3 = st.columns(3)
            
            max_day = daily_df.loc[daily_df['amount'].idxmax()]
            avg_day = daily_df['amount'].mean()
            
            # Next month prediction (Simple)
            predicted_next = avg_month * 1.05 # Simple 5% growth projection
            
            dcol1.metric(get_text(lang, "highest_spending_day"), max_day['date'].strftime('%B %d, %Y'))
            dcol2.metric(get_text(lang, "avg_daily_spending"), f"₹{avg_day:,.0f}")
            dcol3.metric(get_text(lang, "predicted_next_month"), f"₹{predicted_next:,.0f}")

        st.divider()
        predicted, avg = predict_next_month_spending(df)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric(get_text(lang, "predicted_next_month_label"), f"₹{predicted:,.2f}")
        with col_b:
            st.metric(get_text(lang, "daily_average_label"), f"₹{avg:,.2f}")

    # ================== CATEGORIES TAB ==================
    with tab_cats:
        st.markdown(get_text(lang, "category_distribution_header"))
        
        cat_df = df_filtered.groupby("category")["amount"].sum().reset_index()
        cat_df = cat_df.sort_values("amount", ascending=False)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(get_text(lang, "category_breakdown_pie_chart"))
            fig_pie = px.pie(
                cat_df, 
                values="amount", 
                names="category", 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3,
                title=get_text(lang, "category_analysis_header")
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(
                showlegend=True,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_b:
            st.markdown(get_text(lang, "category_hierarchy_treemap"))
            fig_tree = px.treemap(
                df_filtered,
                path=[px.Constant(get_text(lang, "all_spending")), "category", "vendor"],
                values="amount",
                color="amount",
                color_continuous_scale='Viridis',
                title=get_text(lang, "category_hierarchy_title")
            )
            fig_tree.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_tree, use_container_width=True)
        
        # SUMMARY BELOW GRAPHS
        if not cat_df.empty:
            top_category = cat_df.iloc[0]
            lowest_category = cat_df.iloc[-1]
            total_categories = len(cat_df)
            top_3_categories = cat_df.head(3)
            top_3_total = top_3_categories['amount'].sum()
            top_3_percent = (top_3_total / total_spending) * 100
            
            st.markdown(f"""
            <div class="summary-card-orange">
                <div class="metric-label">{get_text(lang, "category_analysis_summary_label")}</div>
                <div class="insight-highlight">
                    🏆 <strong>{get_text(lang, "highest_spending_category")}:</strong> {top_category['category']} - {CURRENCY_SYMBOL}{top_category['amount']:,.2f} ({(top_category['amount']/total_spending*100):.1f}% {get_text(lang, "of_total")})
                </div>
                <div class="insight-highlight">
                    ✅ <strong>{get_text(lang, "lowest_spending_category")}:</strong> {lowest_category['category']} - {CURRENCY_SYMBOL}{lowest_category['amount']:,.2f}
                </div>
                <div class="insight-highlight">
                    📊 <strong>{get_text(lang, "total_categories")}:</strong> {total_categories} {get_text(lang, "different_spending_categories")}
                </div>
                <div class="insight-highlight">
                    💡 <strong>{get_text(lang, "top_3_categories_label")}:</strong> {', '.join(top_3_categories['category'].tolist())} {get_text(lang, "account_for")} {CURRENCY_SYMBOL}{top_3_total:,.2f} ({top_3_percent:.1f}% {get_text(lang, "of_total_spending")})
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ================== VENDORS TAB ==================
    with tab_vendors:
        st.markdown(get_text(lang, "top_vendors_header"))
        
        vendor_df = (
            df_filtered.groupby("vendor")["amount"]
            .agg(['sum', 'count'])
            .reset_index()
            .sort_values("sum", ascending=False)
        )
        vendor_df.columns = ['vendor', 'total_amount', 'transaction_count']

        top_10 = vendor_df.head(10)

        fig_bar = px.bar(
            top_10,
            x="total_amount",
            y="vendor",
            orientation="h",
            title=get_text(lang, "vendor_analysis_header"),
            text="total_amount",
            color="total_amount",
            color_continuous_scale='Sunset',
            labels={'total_amount': get_text(lang, "amount_inr"), 'vendor': get_text(lang, "vendor")}
        )

        fig_bar.update_traces(
            texttemplate=f"{CURRENCY_SYMBOL}"+"%{x:,.0f}",
            textposition="outside"
        )
        
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
            yaxis=dict(showgrid=False),
            showlegend=False
        )

        st.plotly_chart(fig_bar, use_container_width=True)
        
        # SUMMARY BELOW GRAPH
        if not vendor_df.empty:
            top_vendor = vendor_df.iloc[0]
            least_vendor = vendor_df.iloc[-1]
            total_vendors = len(vendor_df)
            avg_per_vendor = vendor_df['total_amount'].mean()
            
            # Most frequent vendor
            most_frequent = vendor_df.loc[vendor_df['transaction_count'].idxmax()]
            
            st.markdown(f"""
            <div class="summary-card-blue">
                <div class="metric-label">🏪 Vendor Analysis</div>
                <div class="insight-highlight">
                    💎 <strong>Highest Paid Vendor:</strong> {top_vendor['vendor']} - ₹{top_vendor['total_amount']:,.2f} ({top_vendor['transaction_count']} transactions)
                </div>
                <div class="insight-highlight">
                    ✅ <strong>Least Paid Vendor:</strong> {least_vendor['vendor']} - ₹{least_vendor['total_amount']:,.2f}
                </div>
                <div class="insight-highlight">
                    🔄 <strong>Most Frequent Vendor:</strong> {most_frequent['vendor']} - {most_frequent['transaction_count']} transactions (₹{most_frequent['total_amount']:,.2f} total)
                </div>
                <div class="insight-highlight">
                    📊 <strong>Total Unique Vendors:</strong> {total_vendors} vendors | Average per vendor: ₹{avg_per_vendor:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ================== ADVANCED TAB ==================
    with tab_advanced:
        st.markdown(get_text(lang, "advanced_analytics_header"))
        
        # Spend concentration
        fig_scatter = px.scatter(
            df_filtered, 
            x='date', 
            y='amount', 
            color='category', 
            size='amount',
            title=get_text(lang, "advanced_analytics_header").replace("### ", ""),
            labels={'date': get_text(lang, "date"), 'amount': get_text(lang, "amount_inr"), 'category': get_text(lang, "category")}
        )
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        fig_box = px.box(
            df_filtered, 
            y="amount", 
            points="all",
            color_discrete_sequence=['#667eea']
        )
        
        fig_box.update_layout(
            title=get_text(lang, "transaction_distribution_title"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
        )
        
        st.plotly_chart(fig_box, use_container_width=True)
        
        # SUMMARY BELOW GRAPH
        if not df_filtered.empty:
            q1 = df_filtered['amount'].quantile(0.25)
            q3 = df_filtered['amount'].quantile(0.75)
            median = df_filtered['amount'].median()
            iqr = q3 - q1
            outlier_threshold = q3 + 1.5 * iqr
            outliers = df_filtered[df_filtered['amount'] > outlier_threshold]
            
            st.markdown(f"""
            <div class="summary-card">
                <div class="metric-label">{get_text(lang, "statistical_analysis_label")}</div>
                <div class="insight-highlight">
                    📈 <strong>{get_text(lang, "median_transaction")}:</strong> ₹{median:,.2f} ({get_text(lang, "middle_value")})
                </div>
                <div class="insight-highlight">
                    📊 <strong>{get_text(lang, "percentile_25")}:</strong> ₹{q1:,.2f} | <strong>{get_text(lang, "percentile_75")}:</strong> ₹{q3:,.2f}
                </div>
                <div class="insight-highlight">
                    🎯 <strong>{get_text(lang, "iqr_label")}:</strong> ₹{iqr:,.2f} ({get_text(lang, "spread_middle_50")})
                </div>
                <div class="insight-highlight">
                    ⚠️ <strong>{get_text(lang, "outliers_detected")}:</strong> {len(outliers)} {get_text(lang, "transactions_above")} ₹{outlier_threshold:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown(get_text(lang, "recurring_patterns_header"))
        st.info(get_text(lang, "recurring_patterns_desc") if "recurring_patterns_desc" in TRANSLATIONS[lang] else "Recurring pattern analysis is coming soon!")
        subs = detect_subscriptions(df)
        if not subs.empty:
            st.dataframe(subs, use_container_width=True)
            
            total_recurring = subs['avg_amount'].sum() if 'avg_amount' in subs.columns else 0
            num_subscriptions = len(subs)
            
            st.markdown(f"""
            <div class="summary-card-green">
                <div class="metric-label">{get_text(lang, "subscription_summary_label")}</div>
                <div class="insight-highlight">
                    📊 <strong>{get_text(lang, "total_subscriptions_detected")}:</strong> {num_subscriptions} {get_text(lang, "recurring_payments")}
                </div>
                <div class="insight-highlight">
                    💰 <strong>{get_text(lang, "estimated_monthly_cost")}:</strong> ₹{total_recurring:,.2f}
                </div>
                <div class="insight-highlight">
                    💡 <strong>{get_text(lang, "tip_review_subscriptions")}:</strong> {get_text(lang, "cancel_unused_services")}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success(get_text(lang, "no_subscriptions_detected"))

    # ================== AI TAB ==================
    with tab_ai:
        st.markdown(get_text(lang, "ai_analysis_header"))
        
        if st.button(get_text(lang, "generate_ai_report_btn"), type="primary", use_container_width=True):
            with st.spinner(get_text(lang, "analyzing_ai")):
                insight = generate_ai_insights(df_filtered, lang=lang)
                st.session_state["ai_insights_cache"] = insight
        
        if "ai_insights_cache" in st.session_state:
            st.markdown(f"#### {get_text(lang, 'ai_insights_header')}")
            st.markdown(f"""
                <div class="summary-card-blue">
                    <div class="metric-label">{get_text(lang, "ai_generated_insights_label")}</div>
                    {st.session_state["ai_insights_cache"]}
                </div>
                """, unsafe_allow_html=True)
