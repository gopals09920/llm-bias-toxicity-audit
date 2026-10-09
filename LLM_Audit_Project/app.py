import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess
import sys

# Page Setup
st.set_page_config(page_title="LLM Audit Engine", layout="wide")

# Main Title
st.title("🛡️ LLM Safety, Toxicity & Bias Audit Dashboard")
st.markdown("Automated Evaluation Framework for Large Language Models")

# Main Screen Re-Run Button Section
col_btn, col_empty = st.columns([1, 3])
with col_btn:
    if st.button("🔄 Re-Run Full Audit Pipeline", type="primary", use_container_width=True):
        with st.spinner("Step 1/2: Generating responses from LLM..."):
            res1 = subprocess.run([sys.executable, "generate_responses.py"])
        
        if res1.returncode == 0:
            with st.spinner("Step 2/2: Calculating Toxicity & Bias Metrics..."):
                res2 = subprocess.run([sys.executable, "audit_engine.py"])
            
            if res2.returncode == 0:
                st.success("✅ Audit Completed Successfully!")
                st.rerun()
            else:
                st.error("❌ Error in Audit Engine execution.")
        else:
            st.error("❌ Error in Response Generation.")

st.markdown("---")

try:
    df = pd.read_csv("audited_results.csv")
    
    # Overview Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Audited Prompts", len(df))
    col2.metric("Average Toxicity Score", f"{df['toxicity_score'].mean():.2f}")
    col3.metric("Average Bias Score", f"{df['bias_score'].mean():.2f}")
    
    high_risk_count = len(df[df['audit_flag'] == 'HIGH BIAS/TOXIC'])
    col4.metric("High Risk Violations", high_risk_count, delta_color="inverse")

    st.markdown("---")

    # Visualizations Section
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📊 Toxicity & Bias Score by Category")
        fig_bar = px.bar(
            df, 
            x="category", 
            y=["toxicity_score", "bias_score"], 
            barmode="group",
            labels={"value": "Score", "variable": "Metric"},
            color_discrete_map={"toxicity_score": "#EF553B", "bias_score": "#636EFA"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("🚦 Risk Flag Distribution")
        fig_pie = px.pie(
            df, 
            names="audit_flag", 
            title="Audit Status (PASS vs HIGH RISK)",
            color="audit_flag",
            color_discrete_map={'PASS': '#00CC96', 'HIGH BIAS/TOXIC': '#EF553B'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Detailed Table View
    st.subheader("📋 Audited Dataset Logs")
    st.dataframe(df, use_container_width=True)

except FileNotFoundError:
    st.error("`audited_results.csv` not found. Click 'Re-Run Full Audit Pipeline' above to generate results.")