# Receipt Vault Analyzer - Enhanced Dashboard UI
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
from database.queries import fetch_all_receipts, delete_receipt  # type: ignore
from ai.insights import generate_ai_insights  # type: ignore
from config.config import CURRENCY_SYMBOL  # type: ignore
from datetime import datetime  # type: ignore
import io  # type: ignore
from reportlab.lib.pagesizes import letter, A4  # type: ignore
from reportlab.lib import colors  # type: ignore
from reportlab.lib.units import inch  # type: ignore
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak  # type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore
from reportlab.lib.enums import TA_CENTER, TA_LEFT  # type: ignore
from config.translations import get_text, TRANSLATIONS # type: ignore


def generate_pdf_report(df):
    """Generate PDF report from dataframe"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
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
    
    lang = st.session_state.get("language", "en")
    # Add title
    title = Paragraph(get_text(lang, "app_name") + " - " + get_text(lang, "export_reports_header").replace("#", "").strip(), title_style)
    elements.append(title)
    
    # Add date
    date_style = ParagraphStyle('DateStyle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)
    date_text = Paragraph(f"{get_text(lang, 'date')}: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", date_style)
    elements.append(date_text)
    elements.append(Spacer(1, 20))
    
    # Summary statistics
    total_spending = df['amount'].sum()
    total_tax = df['tax'].sum()
    total_receipts = len(df)
    avg_transaction = df['amount'].mean()
    
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
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # Add receipts table
    receipt_title = Paragraph(get_text(lang, "stored_receipts_header").replace("#", "").strip(), styles['Heading2'])
    elements.append(receipt_title)
    elements.append(Spacer(1, 12))
    
    # Prepare data for table
    table_data = [[get_text(lang, 'date'), get_text(lang, 'vendor'), get_text(lang, 'bill_id'), get_text(lang, 'subtotal_label'), get_text(lang, 'tax_label'), get_text(lang, 'total_label')]]
    
    for _, row in df.iterrows():
        table_data.append([
            row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else 'N/A',
            str(row['vendor'])[:20],  # Truncate long vendor names
            str(row['bill_id'])[:15],
            f"₹{row['subtotal']:,.2f}",
            f"₹{row['tax']:,.2f}",
            f"₹{row['amount']:,.2f}"
        ])
    
    # Create table
    receipt_table = Table(table_data, colWidths=[1.2*inch, 1.5*inch, 1.2*inch, 1*inch, 0.8*inch, 1*inch])
    receipt_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(receipt_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def render_dashboard():
    lang = st.session_state.get("language", "en")
    st.header(get_text(lang, "dashboard_header"))

    # 1. Fetch Data
    receipts = fetch_all_receipts()
    
    if not receipts:
        st.info(get_text(lang, "no_receipts_found"))
        return

    df = pd.DataFrame(receipts)
    # Ensure date is datetime for better chart handling
    df["date"] = pd.to_datetime(df["date"])
    df_original = df.copy()  # Keep original for export
    df = df.sort_values(by="date", ascending=False)

    # 2. Key Metrics
    total_spend = df["amount"].sum()
    total_tax = df["tax"].sum()
    total_receipts = len(df)
    avg_transaction = df["amount"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(get_text(lang, "total_spending"), f"{CURRENCY_SYMBOL}{total_spend:,.2f}")
    col2.metric(get_text(lang, "total_tax_paid"), f"{CURRENCY_SYMBOL}{total_tax:,.2f}")
    col3.metric(get_text(lang, "receipts_scanned"), total_receipts)
    col4.metric(get_text(lang, "avg_transaction"), f"{CURRENCY_SYMBOL}{avg_transaction:,.2f}")

    st.divider()

    # 3. Export Section
    st.markdown(get_text(lang, "export_reports_header"))
    st.markdown(get_text(lang, "export_reports_subtitle"))
    
    col1, col2, col3, col4 = st.columns(4)
    
    # CSV Export
    with col1:
        csv_data = df_original.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=get_text(lang, "download_csv"),
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
            df_original.to_excel(writer, index=False, sheet_name='Receipts')
            
            # Add a summary sheet
            summary_df = pd.DataFrame({
                'Metric': ['Total Spending', 'Total Tax', 'Total Receipts', 'Average Transaction'],
                'Value': [f'₹{total_spend:,.2f}', f'₹{total_tax:,.2f}', total_receipts, f'₹{avg_transaction:,.2f}']
            })
            summary_df.to_excel(writer, index=False, sheet_name='Summary')
        
        excel_buffer.seek(0)
        st.download_button(
            label=get_text(lang, "download_excel"),
            data=excel_buffer,
            file_name=f"receipts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
    
    # PDF Export
    with col3:
        try:
            pdf_buffer = generate_pdf_report(df_original)
            st.download_button(
                label=get_text(lang, "download_pdf"),
                data=pdf_buffer,
                file_name=f"receipt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
        except Exception as e:
            st.error(f"PDF generation error: {str(e)}")
            st.info("Install reportlab: pip install reportlab")
    
    # JSON Export
    with col4:
        json_data = df_original.to_json(orient='records', date_format='iso', indent=2)
        st.download_button(
            label=get_text(lang, "download_json"),
            data=json_data,
            file_name=f"receipts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
            type="primary"
        )
    
    st.divider()

    # 4. Stored Receipts (Excel-like Scrollable Table)
    st.subheader(get_text(lang, "stored_receipts_header"))
    
    # --- Advanced Filters ---
    st.markdown(get_text(lang, "filter_receipts_header"))
    f1, f2, f3 = st.columns(3)
    with f1:
        sb_bill = st.text_input(get_text(lang, "bill_id_label"), placeholder=get_text(lang, "filter_id_placeholder"))
    with f2:
        sb_vendor = st.text_input(get_text(lang, "vendor_label"), placeholder=get_text(lang, "filter_vendor_placeholder"))
    with f3:
        sb_category = st.selectbox(get_text(lang, "category_label"), [get_text(lang, "all")] + list(df["category"].unique()) if "all" in TRANSLATIONS[lang] else ["All"] + list(df["category"].unique()))
    
    f4, f5, f6 = st.columns(3)
    with f4:
        sb_subtotal = st.text_input(f"{get_text(lang, 'subtotal_label')} ({CURRENCY_SYMBOL})", placeholder=get_text(lang, "filter_subtotal_placeholder"))
    with f5:
        sb_tax = st.text_input(f"{get_text(lang, 'tax_label')} ({CURRENCY_SYMBOL})", placeholder=get_text(lang, "filter_tax_placeholder"))
    with f6:
        sb_amount = st.text_input(f"{get_text(lang, 'total_label')} ({CURRENCY_SYMBOL})", placeholder=get_text(lang, "filter_total_placeholder"))

    if not df.empty:
        # Filtering Logic
        if sb_bill:
            df = df[df["bill_id"].str.lower().str.contains(sb_bill.lower(), na=False)]
        if sb_vendor:
            df = df[df["vendor"].str.lower().str.contains(sb_vendor.lower(), na=False)]
        if sb_category != "All":
            df = df[df["category"] == sb_category]
        if sb_subtotal:
            df = df[df["subtotal"].astype(str).str.contains(sb_subtotal, na=False)]
        if sb_tax:
            df = df[df["tax"].astype(str).str.contains(sb_tax, na=False)]
        if sb_amount:
            df = df[df["amount"].astype(str).str.contains(sb_amount, na=False)]

        # Add a selection column for deletion
        df_display = df.copy()
        df_display.insert(0, "Select", False)
        
        # Format the dataframe for display
        edited_df = st.data_editor(
            df_display,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    get_text(lang, "delete_col"),
                    help=get_text(lang, "delete_help"),
                    default=False,
                ),
                "date": st.column_config.DateColumn(get_text(lang, "date"), format="YYYY-MM-DD"),
                "vendor": get_text(lang, "vendor"),
                "bill_id": get_text(lang, "bill_id"),
                "category": get_text(lang, "category"),
                "subtotal": st.column_config.NumberColumn(f"{get_text(lang, 'subtotal_label')} ({CURRENCY_SYMBOL})", format=f"{CURRENCY_SYMBOL}%.2f"),
                "tax": st.column_config.NumberColumn(f"{get_text(lang, 'tax_label')} ({CURRENCY_SYMBOL})", format=f"{CURRENCY_SYMBOL}%.2f"),
                "amount": st.column_config.NumberColumn(f"{get_text(lang, 'total_label')} ({CURRENCY_SYMBOL})", format=f"{CURRENCY_SYMBOL}%.2f"),
            },
            disabled=["bill_id", "vendor", "date", "amount", "tax", "subtotal", "category"],
            hide_index=True,
            use_container_width=True,
        )

        # Action buttons
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Batch Delete Button
            if st.button(get_text(lang, "delete_selected_btn"), type="secondary", use_container_width=True):
                to_delete = edited_df[edited_df["Select"] == True]
                if not to_delete.empty:
                    for bid in to_delete["bill_id"]:
                        delete_receipt(bid)
                    st.success(get_text(lang, "delete_success").format(len(to_delete)))
                    st.rerun()
                else:
                    st.warning(get_text(lang, "no_receipts_selected"))
        
        with col2:
            st.metric(get_text(lang, "filtered_results"), len(df))
        
        with col3:
            st.metric(get_text(lang, "filtered_total"), f"₹{df['amount'].sum():,.2f}")
    else:
        st.info(get_text(lang, "no_matching_receipts"))

    st.divider()
