import streamlit as st
import pandas as pd
import plotly.express as px

# --- पेज सेटिंग ---
st.set_page_config(page_title="मिश्रा मार्केट", layout="wide")

# डेटा लोड करने का फंक्शन
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
GID = "1626084043" 
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=['Shop_Name'])
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("👑 मिश्रा मार्केट बिलिंग")
    
    # मेन्यू
    choice = st.sidebar.radio("मेन्यू", ["डैशबोर्ड", "पूरी लिस्ट"])

    if choice == "डैशबोर्ड":
        # छोटे कार्ड्स
        c1, c2 = st.columns(2)
        c1.metric("कुल बिल", f"₹{pd.to_numeric(df['Current_Bill'], errors='coerce').sum():,.2f}")
        c2.metric("कुल दुकानें", len(df))
        
        st.divider()
        
        # दुकान चुनें
        shop = st.selectbox("दुकान चुनें", df['Shop_Name'].unique())
        row = df[df['Shop_Name'] == shop].iloc[0]
        
        st.success(f"दुकान: {shop}")
        st.write(f"💵 बिल: ₹{row.get('Current_Bill', 0)}")
        st.write(f"⚠️ बकाया: ₹{row.get('Pending_Balance', 0)}")
        
        # ग्राफ
        fig = px.bar(df, x='Shop_Name', y='Current_Bill', title="सभी दुकानों का बिल")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(df)
else:
    st.error("डेटा नहीं मिला। कृपया शीट चेक करें।")
