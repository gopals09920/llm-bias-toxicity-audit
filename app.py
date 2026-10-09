import streamlit as st
import pandas as pd
import plotly.express as px
from audit_engine import run_audit

st.set_page_config(page_title="LLM Audit Dashboard", layout="wide")

st.title("🛡️ LLM Safety, Toxicity & Bias Audit Dashboard")

uploaded_file = st.file_uploader("📂 Upload Custom Dataset for Batch Audit", type=['csv', 'json'])

if uploaded_file is not None:
    try:
        # File Read
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_json(uploaded_file)
            
        total_file_rows = len(df_raw)
        
        # User Input Box
        num_prompts = st.number_input(
            "Kitne prompts test karne hain?", 
            min_value=1, 
            value=min(10, total_file_rows)
        )

        if st.button("🚀 Run Batch Audit Pipeline"):
            target_limit = int(num_prompts)
            
            # WARNING SIRF TABHI AAYEGI JAB USER MAXIMUM LIMIT CROSS KAREGA
            if target_limit > total_file_rows:
                st.warning(f"⚠️ Warning: Is file mein sirf {total_file_rows} prompts hain! {target_limit} nahi hain, iseliye maximum available {total_file_rows} prompts process ho rahe hain.")
                effective_limit = total_file_rows
            else:
                effective_limit = target_limit

            # Exact Slicing and Audit Execution
            df_selected = df_raw.head(effective_limit).copy()
            df_result = run_audit(df_selected)
            
            # Save to Session State
            st.session_state['df_result'] = df_result
            st.session_state['file_name'] = uploaded_file.name
            st.session_state['count'] = len(df_result)

    except Exception as e:
        st.error(f"File read karne mein error aaya: {e}")
else:
    st.info("Pehle CSV ya JSON file upload karein.")

# DASHBOARD RENDER SECTION
if 'df_result' in st.session_state:
    df_res = st.session_state['df_result']
    
    st.markdown("---")
    st.success(f"✅ Selected top {st.session_state['count']} prompts from {st.session_state['file_name']} for fast testing!")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Audited Prompts", len(df_res))
    col2.metric("Average Toxicity Score", f"{df_res['toxicity_score'].mean():.2f}%")
    col3.metric("Average Bias Score", f"{df_res['bias_score'].mean():.2f}%")
    col4.metric("High Risk Violations", (df_res['audit_flag'] == 'HIGH RISK').sum())

    # Visualizations
    st.markdown("---")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("📊 Toxicity & Bias Score by Category")
        if 'category' in df_res.columns:
            cat_df = df_res.groupby('category')[['toxicity_score', 'bias_score']].mean().reset_index()
            fig_bar = px.bar(cat_df, x='category', y=['toxicity_score', 'bias_score'], barmode='group')
            st.plotly_chart(fig_bar, use_container_width=True)

    with chart_col2:
        st.subheader("🩸 Risk Flag Distribution")
        risk_counts = df_res['audit_flag'].value_counts().reset_index()
        risk_counts.columns = ['Status', 'Count']
        fig_pie = px.pie(risk_counts, values='Count', names='Status', color='Status',
                         color_discrete_map={'PASS': '#2ecc71', 'HIGH RISK': '#e74c3c'})
        st.plotly_chart(fig_pie, use_container_width=True)

    # Detailed Data Table
    st.markdown("---")
    st.subheader("📄 Detailed Audit Logs")
    st.dataframe(df_res, use_container_width=True)