import streamlit as st
import pandas as pd
from groq import Groq

# 🔑 Initialize Groq (use your API key)
import os
client = Groq(api_key=os.getenv("GROQ_API_KEY")) 
# Title
st.title("AI Revenue Copilot 🚀")

# Upload file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # =======================
    # 📊 DATA PREVIEW
    # =======================
    st.subheader("📊 Data Preview")
    st.write(df.head())

    # =======================
    # 📈 KPI METRICS
    # =======================
    st.subheader("📈 Key Metrics")

    numeric_cols = df.select_dtypes(include='number').columns

    if len(numeric_cols) > 0:
        base_revenue = df[numeric_cols[0]].sum()
        avg = df[numeric_cols[0]].mean()

        col1, col2 = st.columns(2)
        col1.metric("Total Revenue", f"{base_revenue:,.0f}")
        col2.metric("Average", f"{avg:,.2f}")

    # =======================
    # 🧠 AUTO INSIGHTS (STEP 3)
    # =======================
    st.subheader("🧠 Auto Business Insights")

    product_col = None
    region_col = None

    for col in df.columns:
        if "product" in col.lower():
            product_col = col
        if "region" in col.lower():
            region_col = col

    revenue_col = numeric_cols[0] if len(numeric_cols) > 0 else None

    if product_col and revenue_col:
        product_perf = df.groupby(product_col)[revenue_col].sum()

        st.write(f"🏆 Best Product: **{product_perf.idxmax()}**")
        st.write(f"⚠️ Needs Attention: **{product_perf.idxmin()}**")

        st.bar_chart(product_perf)

    if region_col and revenue_col:
        region_perf = df.groupby(region_col)[revenue_col].sum()

        st.write(f"🌍 Best Region: **{region_perf.idxmax()}**")
        st.write(f"📉 Weak Region: **{region_perf.idxmin()}**")

        st.bar_chart(region_perf)

    # =======================
    # 📉 DATA VISUALIZATION
    # =======================
    st.subheader("📉 Data Visualization")

    if len(numeric_cols) > 0:
        st.line_chart(df[numeric_cols])

    # =======================
    # 📈 FORECASTING (STEP 4)
    # =======================
    st.subheader("📈 Revenue Forecast")

    if len(numeric_cols) > 0:
        revenue_series = df[numeric_cols[0]]

        forecast = revenue_series.rolling(window=2).mean()
        forecast = forecast.bfill()

        last_value = forecast.iloc[-1]
        future_forecast = [last_value * (1 + 0.05*i) for i in range(1, 4)]

        forecast_extended = list(forecast) + future_forecast

        st.line_chart(forecast_extended)

        st.write(f"🔮 Next Predicted Revenue: **{future_forecast[-1]:,.0f}**")

    # =======================
    # 🤖 FORECAST EXPLANATION
    # =======================
    if st.button("📊 Explain Forecast"):

        forecast_prompt = f"""
        Current Revenue Trend: {list(revenue_series)}

        Predicted Future Revenue: {future_forecast}

        Explain:
        - Trend direction
        - Growth or decline
        - Business recommendation
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": forecast_prompt}]
        )

        st.subheader("🤖 Forecast Insight")
        st.write(response.choices[0].message.content)

    # =======================
    # 🔮 SCENARIO SIMULATOR
    # =======================
    st.subheader("🔮 Scenario Simulator")

    price_change = st.slider("Price Change (%)", -50, 50, 0)
    volume_change = st.slider("Sales Volume Change (%)", -50, 50, 0)

    def simulate_revenue(base, price, volume):
        return base * (1 + price/100) * (1 + volume/100)

    if len(numeric_cols) > 0:
        simulated_revenue = simulate_revenue(base_revenue, price_change, volume_change)

        st.metric("📊 Projected Revenue", f"{simulated_revenue:,.0f}")

    # =======================
    # 🤖 STRATEGY ADVICE
    # =======================
    if st.button("💡 Get Strategy Advice"):

        decision_prompt = f"""
        Base Revenue: {base_revenue}
        Scenario Revenue: {simulated_revenue}

        Price Change: {price_change}%
        Volume Change: {volume_change}%

        As a business strategist:
        - Should we apply this strategy?
        - Risks?
        - Recommendation?
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": decision_prompt}]
        )

        st.subheader("🧠 Strategy Advice")
        st.write(response.choices[0].message.content)

    # =======================
    # ❓ AI Q&A
    # =======================
    st.subheader("❓ Ask AI")

    question = st.text_input("Ask a business question:")

    summary = df.describe(include='all').to_string()
    columns = ", ".join(df.columns)

    if st.button("Get Insight") and question:

        prompt = f"""
        You are a senior business consultant.

        Dataset columns:
        {columns}

        Statistical Summary:
        {summary}

        Question:
        {question}

        Provide:
        - Key Insights
        - Business Risks
        - Recommendations
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        st.subheader("🤖 AI Insight")
        st.write(response.choices[0].message.content)