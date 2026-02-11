from ai.gemini_client import GeminiClient
import streamlit as st
from config.translations import get_text

def generate_ai_insights(df, lang="en") -> str:
    """
    Generate natural language spending insights using Gemini.
    """
    api_key = st.session_state.get("GEMINI_API_KEY")
    if not api_key:
        return get_text(lang, "api_key_missing_msg") if "api_key_missing_msg" in st.session_state else "⚠ Gemini API Key not found. Please add it in the sidebar."

    try:
        client = GeminiClient(api_key)
        
        # optimized summary generation
        if df.empty:
            return get_text(lang, "no_data_analysis")

        total_spend = df["amount"].sum()
        transaction_count = len(df)
        
        top_vendor = df.groupby("vendor")["amount"].sum().idxmax() if not df.empty else "N/A"
        top_category = df.groupby("category")["amount"].sum().idxmax() if "category" in df.columns else "N/A"
        
        # Get last 5 transactions for context
        recent_tx = df.sort_values("date", ascending=False).head(5)[["date", "vendor", "amount", "category"]].to_string(index=False)
        
        # Determine language name for prompt
        lang_names = {
            "en": "English",
            "hi": "Hindi",
            "ta": "Tamil",
            "te": "Telugu",
            "bn": "Bengali",
            "mr": "Marathi"
        }
        target_lang = lang_names.get(lang, "English")

        summary_str = f"""
        Analyze this spending dataset and provide insights IN {target_lang.upper()}:
        
        Dataset Summary:
        - Total Spending: {total_spend:.2f}
        - Total Transactions: {transaction_count}
        - Top Vendor: {top_vendor}
        - Top Category: {top_category}
        - Date Range: {df["date"].min()} to {df["date"].max()}
        
        Recent Transactions:
        {recent_tx}
        
        Please provide 3-4 actionable insights or observations based on this data. Format the output with bullet points.
        """

        return client.generate_insights(summary_str)
    except Exception as e:
        return f"Error generating insights: {str(e)}"
