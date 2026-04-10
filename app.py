import streamlit as st
import pandas as pd
from groq import Groq
import os
from PyPDF2 import PdfReader

# =======================
# 🔑 API
# =======================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =======================
# 💬 CHAT MEMORY
# =======================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =======================
# 🎯 TITLE
# =======================
st.title("🚀 AI Revenue Copilot")

uploaded_file = st.file_uploader("Upload file (Excel or PDF)", type=["xlsx", "pdf"])

# =======================
# 📂 FILE HANDLING
# =======================
if uploaded_file:

    file_type = uploaded_file.name.split(".")[-1]

    # =======================
    # 📊 EXCEL FLOW
    # =======================
    if file_type == "xlsx":

        df = pd.read_excel(uploaded_file)

        # ===== Filters =====
        st.sidebar.header("🔍 Filters")
        filtered_df = df.copy()

        if "Region" in df.columns:
            regions = st.sidebar.multiselect("Region", df["Region"].unique(), df["Region"].unique())
            filtered_df = filtered_df[filtered_df["Region"].isin(regions)]

        if "Product" in df.columns:
            products = st.sidebar.multiselect("Product", df["Product"].unique(), df["Product"].unique())
            filtered_df = filtered_df[filtered_df["Product"].isin(products)]

        # ===== Data =====
        st.subheader("📊 Data Preview")
        st.dataframe(filtered_df)

        numeric_cols = filtered_df.select_dtypes(include='number').columns

        # ===== KPI =====
        if len(numeric_cols) > 0:
            total = filtered_df[numeric_cols[0]].sum()
            avg = filtered_df[numeric_cols[0]].mean()

            col1, col2 = st.columns(2)
            col1.metric("Total Revenue", f"{total:,.0f}")
            col2.metric("Average", f"{avg:,.2f}")

        # ===== Chart =====
        if len(numeric_cols) > 0:
            st.line_chart(filtered_df[numeric_cols])

        # ===== Chat =====
        st.subheader("💬 AI Chat")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("Ask about your data...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            summary = filtered_df.describe().to_string()

            prompt = f"""
            Data Summary:
            {summary}

            Question:
            {user_input}
            """

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            reply = response.choices[0].message.content
            st.chat_message("assistant").markdown(reply)

            st.session_state.messages.append({"role": "assistant", "content": reply})

    # =======================
    # 📄 PDF FLOW (NEW)
    # =======================
    elif file_type == "pdf":

        st.subheader("📄 PDF Analysis")

        pdf = PdfReader(uploaded_file)
        text = ""

        for page in pdf.pages:
            text += page.extract_text()

        st.text_area("Extracted Text Preview", text[:2000])

        st.subheader("🤖 AI Resume / Document Insights")

        if st.button("Analyze PDF with AI"):

            prompt = f"""
            You are an expert business analyst and recruiter.

            Analyze the following document:

            {text[:4000]}

            Provide:
            - Summary
            - Key Skills / Insights
            - Improvement Suggestions
            """

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            st.write(response.choices[0].message.content)