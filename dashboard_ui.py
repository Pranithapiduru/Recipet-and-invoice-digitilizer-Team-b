# Receipt Vault Analyzer - Enhanced Dashboard UI
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
from database.queries import fetch_all_receipts, search_receipts, delete_receipt  # type: ignore
from ai.insights import generate_ai_insights  # type: ignore
from config.config import CURRENCY_SYMBOL  # type: ignore
from datetime import datetime  # type: ignore
import io  # type: ignore
from reportlab.lib.pagesizes import letter, A4  # type: ignore
from reportlab.lib import colors  # type: ignore
from reportlab.lib.units import inch  # type: ignore
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer  # type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore
from reportlab.lib.enums import TA_CENTER  # type: ignore
from config.translations import get_text, TRANSLATIONS # type: ignore


def generate_pdf_report(df, lang="en"):
    """Generate PDF report from dataframe"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Title
    title = Paragraph(get_text(lang, "app_name") + " - Report", title_style)
    elements.append(title)
    
    # Date
    date_style = ParagraphStyle('DateStyle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)
    date_text = Paragraph(f"{get_text(lang, 'date')}: {datetime.now().strftime('%B %d, %Y')}", date_style)
    elements.append(date_text)
    elements.append(Spacer(1, 20))
    
    # Summary Table
    total_spending = df['amount'].sum()
    total_tax = df['tax'].sum()
    total_receipts = len(df)
    avg_transaction = df['amount'].mean() if not df.empty else 0.0
    
    summary_data = [
        ['Metric', 'Value'],
        [get_text(lang, 'total_spending'), f'₹{total_spending:,.2f}'],
        [get_text(lang, 'total_tax_paid'), f'₹{total_tax:,.2f}'],
        [get_text(lang, 'receipts_scanned'), str(total_receipts)],
        [get_text(lang, 'avg_transaction'), f'₹{avg_transaction:,.2f}'],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # Receipts Table
    if not df.empty:
        table_data = [[get_text(lang, 'date'), get_text(lang, 'vendor'), 'Amount']]
        for _, row in df.iterrows():
            table_data.append([
                row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else 'N/A',
                str(row['vendor'])[:20],
                f"₹{row['amount']:,.2f}"
            ])
        
        receipt_table = Table(table_data, colWidths=[2*inch, 3*inch, 2*inch])
        receipt_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(receipt_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def render_dashboard():
    lang = st.session_state.get("language", "en")
    st.markdown(f"## 📊 {get_text(lang, 'dashboard_header')}")

    # --- 1. SEARCH & FILTERS (Server-Side) ---
    with st.expander(f"🔍 {get_text(lang, 'filter_receipts_header')}", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            search_vendor = st.text_input(get_text(lang, "vendor_label"), key="dash_vendor")
        with c2:
            # Need to fetch unique categories efficiently or just strict list
            # For now, simplistic input or pre-defined
            categories = ["All", "Food", "Travel", "Utility", "Grocery", "Shopping", "Medical", "Entertainment", "Uncategorized"]
            search_category = st.selectbox(get_text(lang, "category_label"), categories, key="dash_cat")
        with c3:
             search_date = st.date_input(get_text(lang, "date"), value=None, key="dash_date")

        c4, c5, c6 = st.columns(3)
        with c4:
             min_amt = st.number_input("Min Amount", min_value=0.0, step=10.0, key="dash_min")
        with c5:
             max_amt = st.number_input("Max Amount", min_value=0.0, step=10.0, key="dash_max")
        with c6:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            apply_filters = st.button("🔎 Apply Filters", use_container_width=True, type="primary")

    # Fetch Data based on filters
    if apply_filters or search_vendor or (search_category != "All") or search_date or min_amt or max_amt:
        # Format date string matches
        s_date_str = search_date.strftime("%Y-%m-%d") if search_date else None
        
        receipts = search_receipts(
            vendor=search_vendor,
            category=search_category if search_category != "All" else None,
            min_amount=min_amt if min_amt > 0 else None,
            max_amount=max_amt if max_amt > 0 else None,
            start_date=s_date_str # Simple exact match or start match logic in query
        )
        st.caption(f"Found {len(receipts)} matching receipts")
    else:
        receipts = fetch_all_receipts()

    if not receipts:
        st.info(get_text(lang, "no_receipts_found"))
        return

    df = pd.DataFrame(receipts)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date", ascending=False)
    
    # --- 2. Key Metrics ---
    total_spend = df["amount"].sum()
    total_tax = df["tax"].sum()
    count = len(df)
    avg = df["amount"].mean()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(get_text(lang, "total_spending"), f"{CURRENCY_SYMBOL}{total_spend:,.2f}")
    m2.metric(get_text(lang, "total_tax_paid"), f"{CURRENCY_SYMBOL}{total_tax:,.2f}")
    m3.metric(get_text(lang, "receipts_scanned"), count)
    m4.metric(get_text(lang, "avg_transaction"), f"{CURRENCY_SYMBOL}{avg:,.2f}")

    st.divider()

    # --- 3. Export Section ---
    st.markdown(get_text(lang, "export_reports_header"))
    
    col1, col2, col3, col4 = st.columns(4)
    
    # CSV Export
    with col1:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSV",
            data=csv_data,
            file_name=f"receipts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
    
    # Excel Export
    with col2:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Receipts')
        excel_buffer.seek(0)
        st.download_button(
            label="Excel",
            data=excel_buffer,
            file_name=f"receipts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
    
    # PDF Export
    with col3:
        try:
            pdf_buffer = generate_pdf_report(df, lang)
            st.download_button(
                label="PDF",
                data=pdf_buffer,
                file_name=f"receipt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
        except Exception as e:
            st.error(f"PDF Error: {str(e)}")
    
    # JSON Export
    with col4:
        json_data = df.to_json(orient='records', date_format='iso', indent=2)
        st.download_button(
            label="JSON",
            data=json_data,
            file_name=f"receipts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
            type="primary"
        )
    
    st.divider()

    # --- 4. Data Table & Actions ---
    st.subheader(get_text(lang, "stored_receipts_header"))
    
    # Selection/Delete
    df_display = df.copy()
    df_display.insert(0, "Select", False)
    
    edited_df = st.data_editor(
        df_display,
        column_config={
            "Select": st.column_config.CheckboxColumn(required=True),
            "date": st.column_config.DateColumn(get_text(lang, "date"), format="YYYY-MM-DD"),
            "amount": st.column_config.NumberColumn(format=f"{CURRENCY_SYMBOL}%.2f"),
            "tax": st.column_config.NumberColumn(format=f"{CURRENCY_SYMBOL}%.2f"),
        },
        disabled=["bill_id", "vendor", "date", "amount", "tax", "category"],
        hide_index=True,
        use_container_width=True,
        key="dashboard_editor"
    )

    col_actions, _ = st.columns([1, 1])
    
    with col_actions:
        if st.button(get_text(lang, "delete_selected_btn"), type="secondary"):
            to_delete = edited_df[edited_df["Select"] == True]
            if not to_delete.empty:
                for bid in to_delete["bill_id"]:
                    delete_receipt(bid)
                st.success(f"Deleted {len(to_delete)} receipts!")
                st.rerun()
            else:
                st.warning("Select receipts to delete")