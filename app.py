import streamlit as st
import pandas as pd
from groq import Groq
from PyPDF2 import PdfReader

# =======================
# 🔑 CONFIG
# =======================
st.set_page_config(page_title="AI Revenue Copilot", layout="wide")

# =======================
# 🔑 API (FIXED)
# =======================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# =======================
# 💬 CHAT MEMORY
# =======================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =======================
# 🎯 SIDEBAR
# =======================
st.sidebar.title("👨‍💼 Sonu Verma")
st.sidebar.markdown("**AI Transformation Consultant**")
st.sidebar.markdown("GenAI | RAG | Business Analytics")
st.sidebar.markdown("14+ Years Experience")

st.sidebar.markdown("---")

st.sidebar.markdown("📧 sonuverma9560@gmail.com")
st.sidebar.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/sonu-verma-data-science-business-analyst-iiit-bangalore)")
st.sidebar.markdown("💻 [GitHub](https://github.com/sonuverma9560/ai-revenue-copilot)")

st.sidebar.markdown("---")

menu = st.sidebar.radio("📌 Select Option", ["Excel Analysis", "PDF Analysis"])

st.sidebar.success("🚀 Live AI Project")

# =======================
# 🎯 TITLE
# =======================
st.markdown("# 🚀 AI Revenue Copilot")
st.markdown("### 📊 AI-powered Business Insights Platform")

uploaded_file = st.file_uploader("Upload file (Excel or PDF)", type=["xlsx", "pdf"])

# =======================
# 📊 EXCEL ANALYSIS
# =======================
if menu == "Excel Analysis" and uploaded_file:

    if uploaded_file.name.endswith("xlsx"):

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

        # ===== Data Preview =====
        st.subheader("📊 Data Preview")
        st.dataframe(filtered_df)

        numeric_cols = filtered_df.select_dtypes(include='number').columns

        # ===== KPI =====
        if len(numeric_cols) > 0:
            total = filtered_df[numeric_cols[0]].sum()
            avg = filtered_df[numeric_cols[0]].mean()

            col1, col2, col3 = st.columns(3)
            col1.metric("📈 Total", f"{total:,.0f}")
            col2.metric("📊 Average", f"{avg:,.2f}")
            col3.metric("📦 Records", len(filtered_df))

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

            with st.spinner("🤖 Thinking..."):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    reply = response.choices[0].message.content
                except:
                    reply = "⚠️ API Error — check key"

            st.chat_message("assistant").markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # ===== Download =====
            st.download_button("⬇ Download Insights", reply)

# =======================
# 📄 PDF ANALYSIS
# =======================
elif menu == "PDF Analysis" and uploaded_file:

    if uploaded_file.name.endswith("pdf"):

        st.subheader("📄 PDF Analysis")

        pdf = PdfReader(uploaded_file)
        text = ""

        for page in pdf.pages:
            text += page.extract_text()

        st.text_area("Extracted Text Preview", text[:2000])

        if st.button("Analyze PDF with AI"):

            prompt = f"""
            You are an expert business analyst.

            Analyze this document:

            {text[:4000]}

            Provide:
            - Summary
            - Key Insights
            - Suggestions
            """

            with st.spinner("🤖 Analyzing..."):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    reply = response.choices[0].message.content
                except:
                    reply = "⚠️ API Error — check key"

            st.write(reply)

            # ===== Download =====
            st.download_button("⬇ Download Report", reply)