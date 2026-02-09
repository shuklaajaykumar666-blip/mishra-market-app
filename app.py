import streamlit as st
import pandas as pd

# --- पेज सेटिंग ---
st.set_page_config(page_title="Mishra Market Billing", layout="wide")
st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग")

# आपकी शीट की ID
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"

# सीधे पूरी शीट को खींचने का सबसे आसान तरीका
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def load_data():
    try:
        # डेटा लोड करना
        df = pd.read_csv(CSV_URL)
        # कॉलम के आसपास के फालतू स्पेस हटाना
        df.columns = df.columns.str.strip()
        # अगर Shop_Name वाला कॉलम है, तो ही आगे बढ़ना
        if 'Shop_Name' in df.columns:
            df = df.dropna(subset=['Shop_Name'])
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# अगर डेटा मिल गया
if not df.empty:
    tab1, tab2 = st.tabs(["📊 बिलिंग डैशबोर्ड", "📋 पूरी लिस्ट"])

    with tab1:
        st.subheader("दुकान चुनें")
        # कॉलम का नाम सही से पहचानना
        s_col = 'Shop_Name' if 'Shop_Name' in df.columns else df.columns[0]
        shop_list = df[s_col].unique().tolist()
        selected_shop = st.selectbox("लिस्ट में से नाम चुनें:", shop_list)

        # डेटा फिल्टर करना
        shop_data = df[df[s_col] == selected_shop].iloc[0]

        # कार्ड डिजाइन
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("कुल बिल", f"₹{shop_data.get('Total_Amount', 0)}")
        with c2:
            st.metric("यूनिट्स", f"{shop_data.get('Units_Used', 0)}")
        with c3:
            st.metric("बकाया", f"₹{shop_data.get('Pending Balance', 0)}")

        st.divider()
        
        # विस्तृत जानकारी
        col_a, col_b = st.columns(2)
        with col_a:
            st.info(f"📱 WhatsApp: {shop_data.get('WhatsApp No', 'N/A')}")
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
    st.error("❌ डेटा नहीं मिला! कृपया चेक करें कि आपकी शीट की पहली लाइन (Row 1) में 'Shop_Name' लिखा है या नहीं।")
    st.info("सुझाव: Google Sheet में Share बटन दबाकर 'Anyone with the link' को 'Editor' सेट करें।")

st.sidebar.success("✅ सिस्टम एक्टिव है")
