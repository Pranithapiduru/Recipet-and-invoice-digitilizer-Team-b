import streamlit as st
import requests
import json
from config.translations import get_text
from datetime import datetime

def render_api_ui():
    lang = st.session_state.get("language", "en")
    st.header("🔗 ERP Integration & API")
    st.info("Directly connect your extracted receipt data to external systems like SAP, Oracle, or NetSuite.")

    # API Status Check
    st.subheader("📡 Global API Status")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        **Base Endpoint:** `http://localhost:8000/api/v1`  
        **Docs:** [Swagger UI](http://localhost:8000/docs)  
        **Auth:** Default (API Key Required in Production)
        """)
        
    with col2:
        try:
            # Quick health check (simulated if server not running in background)
            response = requests.get("http://localhost:8000/", timeout=1)
            if response.status_code == 200:
                st.success("● API ONLINE")
            else:
                st.warning("● API STARTING")
        except:
            st.error("● API OFFLINE (Run `python api/main.py` to start)")

    st.divider()

    # ERP Configuration
    st.subheader("🏢 ERP Configuration")
    erp_system = st.selectbox("Select Target ERP System", ["ERPNext", "SAP S/4HANA", "Oracle NetSuite", "Microsoft Dynamics 365", "Generic REST Webhook"])
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.text_input("ERP Endpoint URL", value="https://erp.enterprise.com/api/ingest")
    with col_b:
        st.text_input("Client ID / API Secret", type="password", value="**************")

    # Simulation / Sync
    if st.button("🚀 Trigger Manual ERP Sync", type="primary", use_container_width=True):
        with st.spinner(f"Mapping and transmitting data to {erp_system}..."):
            try:
                # Mock a call to our own local API to get the ERP payload
                # We use a POST to simulate a transformation
                res = requests.post("http://localhost:8000/api/v1/erp/sync", params={"system": erp_system}, timeout=5)
                if res.status_code == 200:
                    result = res.json()
                    st.success(f"Successfully synced {result['exported_records']} records to {erp_system}")
                    
                    with st.expander("📄 View Transmitted ERP Payload (JSON)"):
                        st.json(result["payload_preview"])
                else:
                    st.error("Failed to fetch ERP payload from API.")
            except Exception as e:
                st.error("Could not reach the Synchronization API. Please ensure the backend is running.")

    st.divider()
    
    # API Documentation Preview
    st.subheader("📚 Integration Guide")
    st.markdown(f"""
    To fetch data for your accounting software, use the following payload structure:
    ```bash
    curl -X GET "http://localhost:8000/api/v1/receipts?vendor=Amazon" \\
         -H "accept: application/json"
    ```
    
    **ERP Mapping Logic:**
    - `ExternalInvID` maps to **Bill ID**.
    - `Supplier` maps to **Vendor**.
    - `PostingDate` maps to **Date**.
    - `GrossAmount` maps to **Total Amount**.
    """)

if __name__ == "__main__":
    render_api_ui()
