import streamlit as st
import pandas as pd
from groq import Groq
from PyPDF2 import PdfReader

# =======================
# 🔑 API (DEPLOY SAFE)
# =======================
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

# =======================
# 💬 CHAT MEMORY
# =======================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =======================
# 🎯 TITLE
# =======================
st.title("🚀 AI Revenue Copilot")

# =======================
# 📌 SIDEBAR (PROFILE)
# =======================
st.sidebar.title("👨‍💼 Sonu Verma")

st.sidebar.markdown("""
**AI Transformation Consultant**  
GenAI | RAG | Business Analytics  
14+ Years Experience  
""")

st.sidebar.markdown("📧 sonuverma9560@gmail.com")
st.sidebar.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/sonu-verma-data-science-business-analyst-iiit-bangalore)")
st.sidebar.markdown("💻 [GitHub](https://github.com/sonuverma9560/ai-revenue-copilot)")
st.sidebar.divider()

# =======================
# 📊 MENU
# =======================
menu = st.sidebar.radio("Select Option", ["Excel Analysis", "PDF Analysis"])

# =======================
# 📂 FILE UPLOAD
# =======================
uploaded_file = st.file_uploader("Upload file (Excel or PDF)", type=["xlsx", "pdf"])

# =======================
# 📊 EXCEL FLOW
# =======================
if menu == "Excel Analysis" and uploaded_file:

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

        summary = filtered_df.describe().to_string()[:2000]

        prompt = f"""
        You are a financial analyst.

        Analyze this dataset summary:
        {summary}

        Answer clearly with business insights.

        Question:
        {user_input}
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        reply = response.choices[0].message.content

        st.chat_message("assistant").markdown(reply)

        # ===== Download =====
        st.download_button("Download Result", reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

# =======================
# 📄 PDF FLOW
# =======================
elif menu == "PDF Analysis" and uploaded_file:

    st.subheader("📄 PDF Analysis")

    pdf = PdfReader(uploaded_file)
    text = ""

    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    st.text_area("Extracted Text Preview", text[:2000])

    st.subheader("🤖 AI Document Insights")

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

        result = response.choices[0].message.content

        st.write(result)

        # ===== Download =====
        st.download_button("Download Report", result)