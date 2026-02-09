import streamlit as st
import pandas as pd

# --- पेज सेटिंग ---
st.set_page_config(page_title="Mishra Market Billing", layout="wide")
st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग")

# आपकी शीट की ID
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"

# यहाँ अपने शीट के टैब (Tab) का नाम लिखें (जैसे: Billing_Data)
# अगर आप नाम बदलें, तो यहाँ भी बदल दें
SHEET_NAME = "Billing_Data" 

# गूगल शीट से डेटा लाने का लिंक (टैब नाम के साथ)
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

def load_data():
    try:
        # डेटा लोड करना
        df = pd.read_csv(CSV_URL)
        # कॉलम के आसपास के फालतू स्पेस हटाना
        df.columns = df.columns.str.strip()
        # खाली रो हटाना
        df = df.dropna(subset=['Shop_Name'])
        return df
    except Exception as e:
        st.error(f"शीट से डेटा नहीं मिल रहा। कृपया टैब का नाम चेक करें: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- मुख्य स्क्रीन ---
    tab1, tab2 = st.tabs(["📊 बिलिंग डैशबोर्ड", "📋 पूरी लिस्ट"])

    with tab1:
        st.subheader("दुकान चुनें")
        shop_list = df['Shop_Name'].unique().tolist()
        selected_shop = st.selectbox("लिस्ट में से नाम चुनें:", shop_list)

        # चुनी हुई दुकान का डेटा
        shop_data = df[df['Shop_Name'] == selected_shop].iloc[0]

        # कार्ड डिजाइन में डेटा दिखाना
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
    st.info("डेटा लोड हो रहा है या शीट खाली है...")

st.sidebar.success("✅ डेटाबेस लिंक है")
