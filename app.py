import streamlit as st
import pandas as pd

# --- पेज सेटिंग ---
st.set_page_config(page_title="Mishra Market Billing", layout="wide")
st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग")

# आपकी शीट की ID
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"

# गूगल का सबसे पावरफुल डेटा लिंक (Visualization API)
# यह लिंक सीधे डेटा को टेबल के रूप में उठाता है
QUERY_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

def load_data():
    try:
        # डेटा लोड करना
        df = pd.read_csv(QUERY_URL)
        # अगर कॉलम के नाम में फालतू स्पेस या 'Unnamed' है तो उसे ठीक करना
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df.columns = df.columns.str.strip()
        
        # पक्का करें कि Shop_Name वाला कॉलम है
        if 'Shop_Name' in df.columns:
            df = df.dropna(subset=['Shop_Name'])
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# अगर डेटा मिल गया
if not df.empty and len(df.columns) > 1:
    tab1, tab2 = st.tabs(["📊 बिलिंग डैशबोर्ड", "📋 पूरी लिस्ट"])

    with tab1:
        st.subheader("दुकान चुनें")
        # कॉलम ढूंढना (चाहे नाम कुछ भी हो, पहला कॉलम दुकान का नाम मानेंगे)
        shop_col = 'Shop_Name' if 'Shop_Name' in df.columns else df.columns[0]
        
        shop_list = df[shop_col].unique().tolist()
        selected_shop = st.selectbox("लिस्ट में से दुकानदार का नाम चुनें:", shop_list)

        # डेटा फिल्टर करना
        shop_data = df[df[shop_col] == selected_shop].iloc[0]

        # कार्ड डिजाइन
        c1, c2, c3 = st.columns(3)
        with c1:
            val = shop_data.get('Total_Amount', shop_data.get('Total Amount', 0))
            st.metric("कुल बिल", f"₹{val}")
        with c2:
            val = shop_data.get('Units_Used', shop_data.get('Units Used', 0))
            st.metric("यूनिट्स", f"{val}")
        with c3:
            val = shop_data.get('Pending Balance', shop_data.get('Pending_Balance', 0))
            st.metric("बकाया", f"₹{val}")

        st.divider()
        
        # विस्तृत जानकारी
        col_a, col_b = st.columns(2)
        with col_a:
            st.info(f"📱 WhatsApp: {shop_data.get('WhatsApp No', shop_data.get('WhatsApp_No', 'N/A'))}")
            st.write(f"📉 पुरानी रीडिंग: {shop_data.get('Prev_Reading', 0)}")
            st.write(f"📈 नई रीडिंग: {shop_data.get('Curr_Reading', 0)}")
        
        with col_b:
            st.success(f"स्थिति: {shop_data.get('Status', 'Pending')}")
            st.write(f"⚡ यूनिट रेट: ₹{shop_data.get('Effective_Unit_Rate', 0)}")
            st.write(f"🛠 फिक्स चार्ज: ₹{shop_data.get('Fix_Charge', 0)}")

    with tab2:
        st.subheader("सभी दुकानों का डेटा")
        st.dataframe(df)
else:
    st.error("❌ अभी भी डेटा नहीं दिख रहा!")
    st.write("राजा साहब, एक बार चेक करें कि आपकी शीट में **कम से कम एक दुकान का नाम** लिखा है या नहीं।")
    st.info("अगर शीट में डेटा है, तो एक बार 'Manage App' में जाकर 'Reboot' बटन दबाएं।")

st.sidebar.success("✅ सिस्टम एक्टिव है")
