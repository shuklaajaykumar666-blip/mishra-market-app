import streamlit as st
import pandas as pd
import plotly.express as px

# पेज सेटिंग
st.set_page_config(page_title="Mishra Market", layout="wide")

# --- लिंक का नया और पक्का तरीका ---
# हम सीधे 'pub' (पब्लिश) लिंक का इस्तेमाल करेंगे जो कभी फेल नहीं होता
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
# SHOP_DATA का GID
GID = "1626084043"

# नया CSV लिंक फॉर्मेट
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?gid={GID}&format=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        # डेटा पढ़ना
        df = pd.read_csv(CSV_URL)
        # कॉलम के नाम से फालतू स्पेस हटाना
        df.columns = df.columns.str.strip()
        # खाली नाम वाली लाइनें हटाना
        df = df.dropna(subset=['Shop_Name'])
        return df
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame()

# --- ऐप का मुख्य हिस्सा ---
try:
    df = load_data()
    
    if not df.empty:
        st.title("👑 मिश्रा मार्केट बिलिंग")
        
        # मुख्य मेट्रिक्स
        st.subheader("📊 बाज़ार का सारांश")
        df['Current_Bill'] = pd.to_numeric(df['Current_Bill'], errors='coerce').fillna(0)
        
        c1, c2 = st.columns(2)
        c1.metric("कुल बिल राशि", f"₹{df['Current_Bill'].sum():,.2f}")
        c2.metric("कुल दुकानें", len(df))

        st.divider()

        # चार्ट
        fig = px.bar(df, x='Shop_Name', y='Current_Bill', color='Current_Bill', title="दुकान वार बिल ग्राफ")
        st.plotly_chart(fig, use_container_width=True)

        # लिस्ट
        st.subheader("📋 दुकानदार सूची")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("शीट मिल गई है, लेकिन उसमें डेटा नहीं दिख रहा।")

except Exception as e:
    st.error(f"कनेक्शन एरर: {e}")
