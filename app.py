import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# --- पेज सेटअप ---
st.set_page_config(page_title="मिश्रा मार्केट", layout="wide")

# डेटा लोड करने का फंक्शन (बिना किसी एक्स्ट्रा पैकेज के)
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
GID = "1626084043" 
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=['Shop_Name'])
        # नंबर वाले कॉलम्स को ठीक करना
        cols = ['Current_Bill', 'Units_Used', 'Pending_Balance']
        for c in cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"शीट से डेटा नहीं मिल रहा: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग")
    
    # साइडबार मेन्यू
    menu = st.sidebar.radio("मेन्यू", ["📊 डैशबोर्ड", "🧾 बिल रसीद", "📋 पूरी लिस्ट"])

    if menu == "📊 डैशबोर्ड":
        c1, c2, c3 = st.columns(3)
        c1.metric("कुल बिल", f"₹{df['Current_Bill'].sum():,.2f}")
        c2.metric("कुल बकाया", f"₹{df['Pending_Balance'].sum():,.2f}")
        c3.metric("कुल दुकानें", len(df))
        
        st.divider()
        fig = px.bar(df, x='Shop_Name', y='Current_Bill', color='Current_Bill', title="दुकान वार बिल")
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "🧾 बिल रसीद":
        shop = st.selectbox("दुकान चुनें", df['Shop_Name'].unique())
        row = df[df['Shop_Name'] == shop].iloc[0]
        
        st.info(f"📍 दुकान: {shop}")
        st.success(f"💵 इस महीने का बिल: ₹{row['Current_Bill']}")
        st.error(f"⚠️ बकाया राशि: ₹{row['Pending_Balance']}")
        
        # व्हाट्सएप बटन
        total = row['Current_Bill'] + row['Pending_Balance']
        msg = f"नमस्ते {shop}, आपका बिल: ₹{row['Current_Bill']}, बकाया: ₹{row['Pending_Balance']}, कुल: ₹{total}."
        wa_url = f"https://wa.me/91{row['WhatsApp_No']}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366;color:white;padding:10px;border:none;border-radius:5px;">WhatsApp भेजें</button></a>', unsafe_allow_html=True)

    else:
        st.dataframe(df)
else:
    st.warning("डेटा लोड हो रहा है या शीट खाली है...")
