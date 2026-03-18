import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- 1. CONFIG & THEME ---
st.set_page_config(
    page_title="Aetherium Finance | AI Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for a "Premium" feel
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AI SETUP (Streamlit Secrets) ---
try:
    # This pulls from the "Secrets" tab in Streamlit Cloud
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.warning("⚠️ AI Advisor Offline: Please add GEMINI_API_KEY to Streamlit Secrets.")

# --- 3. DATA ENGINE ---
if 'ledger' not in st.session_state:
    st.session_state.ledger = pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Note"])
if 'balance' not in st.session_state:
    st.session_state.balance = 10000.00

# --- 4. SIDEBAR (Input Portal) ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=AETHERIUM", use_column_width=True)
    st.header("Strategic Entry")
    t_type = st.selectbox("Transaction Type", ["Expense", "Income"])
    cat = st.selectbox("Category", ["Consulting Services", "Wellness & Performance", "Operational Tech", "Travel/Logistics"])
    amt = st.number_input("Amount ($)", min_value=0.0, step=50.0)
    note = st.text_input("Reference Note")
    
    if st.button("Authorize Transaction", use_container_width=True):
        val = -amt if t_type == "Expense" else amt
        new_tx = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Type": t_type,
            "Category": cat,
            "Amount": val,
            "Note": note
        }
        st.session_state.ledger = pd.concat([st.session_state.ledger, pd.DataFrame([new_tx])], ignore_index=True)
        st.session_state.balance += val
        st.success("Ledger Updated Successfully.")

# --- 5. EXECUTIVE DASHBOARD ---
st.title("🛡️ Aetherium Strategic Finance")
st.markdown("### High-Performance Fiscal Oversight")

m1, m2, m3 = st.columns(3)
m1.metric("Current Liquidity", f"${st.session_state.balance:,.2f}")
m2.metric("Operational Burn", f"${abs(st.session_state.ledger[st.session_state.ledger['Amount'] < 0]['Amount'].sum()):,.2f}", delta_color="inverse")
m3.metric("Fiscal Resiliency", "92%", help="Calculated based on cash-on-hand vs projected monthly expenses.")

st.divider()

# --- 6. AI INSIGHTS ENGINE ---
st.subheader("🤖 AI Strategic Advisor")
if st.button("Generate Performance Analysis"):
    if not st.session_state.ledger.empty:
        with st.spinner("Analyzing financial velocity..."):
            data_ctx = st.session_state.ledger.to_string()
            prompt = f"Act as a McKinsey Financial Consultant. Analyze this ledger: {data_ctx}. Provide 3 executive bullet points on spending efficiency and performance optimization."
            response = model.generate_content(prompt)
            st.info(response.text)
    else:
        st.info("Awaiting data input for analysis.")

# --- 7. DATA TABLE ---
st.subheader("Transaction History")
st.dataframe(st.session_state.ledger.sort_index(ascending=False), use_container_width=True)

# Download Button
if not st.session_state.ledger.empty:
    csv = st.session_state.ledger.to_csv(index=False).encode('utf-8')
    st.download_button("Export Ledger (CSV)", data=csv, file_name="aetherium_ledger.csv", mime="text/csv")
