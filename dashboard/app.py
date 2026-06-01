import os

import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

API_URL = os.getenv("API_URL", "http://app:8000")

st.set_page_config(page_title="FinSight", page_icon="📈", layout="wide")

st.title("FinSight — Portfolio Risk Analytics")
st.caption("Real-time risk metrics and fraud detection for your financial portfolio")

with st.sidebar:
    st.header("Portfolio")
    portfolio_id = st.text_input("Portfolio ID (UUID)", placeholder="Paste portfolio UUID here")
    analyze = st.button("Analyze", type="primary", use_container_width=True)

    st.divider()
    st.subheader("Create Portfolio")
    new_user_id = st.text_input("User ID")
    new_name = st.text_input("Portfolio Name")
    if st.button("Create", use_container_width=True):
        if new_user_id and new_name:
            r = httpx.post(f"{API_URL}/api/v1/portfolio/", json={"user_id": new_user_id, "name": new_name})
            if r.status_code == 201:
                data = r.json()
                st.success(f"Created! ID: `{data['id']}`")
                st.code(data["id"])
            else:
                st.error(r.text)

if portfolio_id and analyze:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Risk Metrics")
        with st.spinner("Computing risk metrics..."):
            r = httpx.get(f"{API_URL}/api/v1/risk/{portfolio_id}", timeout=30)

        if r.status_code == 200:
            m = r.json()
            c1, c2, c3 = st.columns(3)
            c1.metric("Portfolio Value", f"${m['portfolio_value']:,.2f}")
            c2.metric("Sharpe Ratio", f"{m['sharpe_ratio']:.4f}")
            c3.metric("Ann. Volatility", f"{m['annualized_volatility']:.2%}")

            c4, c5, c6 = st.columns(3)
            c4.metric("VaR 95% (1-day)", f"{m['var_95']:.2%}")
            c5.metric("VaR 99% (1-day)", f"{m['var_99']:.2%}")
            c6.metric("Max Drawdown", f"{m['max_drawdown']:.2%}")

            fig = go.Figure(
                go.Bar(
                    x=["VaR 95%", "VaR 99%", "Max Drawdown"],
                    y=[m["var_95"], m["var_99"], m["max_drawdown"]],
                    marker_color=["#ef553b", "#ab63fa", "#636efa"],
                )
            )
            fig.update_layout(title="Downside Risk Metrics", yaxis_tickformat=".2%", height=300)
            st.plotly_chart(fig, use_container_width=True)
        elif r.status_code == 404:
            st.warning("No transactions found. Add transactions first.")
        else:
            st.error(f"Error: {r.text}")

    with col2:
        st.subheader("Transactions")
        r2 = httpx.get(f"{API_URL}/api/v1/transactions/portfolio/{portfolio_id}", timeout=15)
        if r2.status_code == 200:
            txns = r2.json()
            if txns:
                df = pd.DataFrame(txns)
                df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
                df["notional"] = df["quantity"] * df["price"]

                fraud_counts = df["is_flagged"].value_counts()
                if len(fraud_counts) > 1:
                    fig2 = px.pie(
                        values=fraud_counts.values,
                        names=fraud_counts.index,
                        title="Fraud Assessment",
                        color_discrete_map={"clean": "#00cc96", "suspicious": "#ffa15a", "fraud": "#ef553b"},
                    )
                    fig2.update_layout(height=250)
                    st.plotly_chart(fig2, use_container_width=True)

                st.dataframe(
                    df[["symbol", "quantity", "price", "notional", "transaction_type", "is_flagged", "timestamp"]],
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.info("No transactions yet.")

st.divider()
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Add Transaction")
    with st.form("add_txn"):
        pid = st.text_input("Portfolio ID")
        sym = st.text_input("Symbol (e.g. AAPL)").upper()
        qty = st.number_input("Quantity", min_value=0.01, value=10.0)
        price = st.number_input("Price ($)", min_value=0.01, value=150.0)
        txn_type = st.selectbox("Type", ["BUY", "SELL"])
        submitted = st.form_submit_button("Submit Transaction")

        if submitted and pid and sym:
            r = httpx.post(
                f"{API_URL}/api/v1/transactions/",
                json={"portfolio_id": pid, "symbol": sym, "quantity": qty, "price": price, "transaction_type": txn_type},
                timeout=15,
            )
            if r.status_code == 201:
                result = r.json()
                fa = result["fraud_assessment"]
                if fa["label"] == "clean":
                    st.success(f"Transaction added. Fraud score: {fa['anomaly_score']}")
                else:
                    st.error(f"FRAUD ALERT — label: {fa['label']}, score: {fa['anomaly_score']}")
            else:
                st.error(r.text)

with col_b:
    st.subheader("API Status")
    try:
        r = httpx.get(f"{API_URL}/health", timeout=5)
        if r.status_code == 200:
            st.success("API: Online")
        else:
            st.error("API: Degraded")
    except Exception:
        st.error("API: Offline")
    st.caption(f"API endpoint: `{API_URL}`")
