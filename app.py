import streamlit as st
import pandas as pd
import plotly.express as px

# पेज सेटअप
st.set_page_config(page_title="Mishra Market", layout="wide")

# डेटा लिंक
URL = "https://docs.google.com/spreadsheets/d/19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo/export?format=csv&gid=1626084043"

@st.cache_data(ttl=60)
def load():
    df = pd.read_csv(URL)
    df.columns = df.columns.str.strip()
    return df.dropna(subset=['Shop_Name'])

try:
    df = load()
    st.title("👑 मिश्रा मार्केट बिलिंग")
    
    # ग्राफ
    st.subheader("📊 मार्केट की स्थिति")
    df['Current_Bill'] = pd.to_numeric(df['Current_Bill'], errors='coerce').fillna(0)
    fig = px.bar(df, x='Shop_Name', y='Current_Bill', color='Shop_Name')
    st.plotly_chart(fig, use_container_width=True)

    # टेबल
    st.subheader("📋 पूरी लिस्ट")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
