import streamlit as st
import pandas as pd
import plotly.express as px

# --- पेज सेटिंग ---
st.set_page_config(page_title="मिश्रा मार्केट डैशबोर्ड", layout="wide")
st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग")

# आपकी शीट की ID
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
# SHOP_DATA का पक्का GID
GID = "1626084043" 

# डेटा लाने का लिंक
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip()
        # खाली रो हटाना
        df = df.dropna(subset=['Shop_Name'])
        # नंबर वाले कॉलम को सही करना
        cols_to_fix = ['Current_Bill', 'Units_Used', 'Pending_Balance']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- ऊपर के आंकड़े (Metrics) ---
    t1, t2, t3 = st.columns(3)
    with t1:
        st.metric("कुल मासिक बिल", f"₹{df['Current_Bill'].sum():,.2f}")
    with t2:
        st.metric("कुल बकाया", f"₹{df['Pending_Balance'].sum():,.2f}")
    with t3:
        st.metric("कुल दुकानें", len(df))

    st.divider()

    # --- दो हिस्से: बिल और चार्ट ---
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📍 दुकानदार का विवरण")
        shop_list = df['Shop_Name'].unique().tolist()
        selected_shop = st.selectbox("नाम चुनें:", shop_list)
        
        data = df[df['Shop_Name'] == selected_shop].iloc[0]
        
        st.info(f"📱 WhatsApp: {data.get('WhatsApp_No', 'N/A')}")
        st.write(f"📉 पुरानी रीडिंग: {data.get('Prev_Reading', 0)}")
        st.write(f"📈 नई रीडिंग: {data.get('Curr_Reading', 0)}")
        st.success(f"💵 इस महीने का बिल: ₹{data.get('Current_Bill', 0)}")
        st.error(f"⚠️ पुराना बकाया: ₹{data.get('Pending_Balance', 0)}")

    with col_right:
        st.subheader("📊 बिल ग्राफ")
        # छोटा ग्राफ
        fig = px.bar(df, x='Shop_Name', y='Current_Bill', color='Current_Bill')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 पूरी लिस्ट")
    st.dataframe(df)

else:
    st.error("डेटा लोड नहीं हो पाया! कृपया GitHub पर कोड अपडेट करें और Reboot दबाएँ।")

st.sidebar.success("सिस्टम ऑनलाइन है")
