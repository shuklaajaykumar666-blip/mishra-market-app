import streamlit as st
import pandas as pd

# --- पेज सेटिंग ---
st.set_page_config(page_title="Mishra Market Billing", layout="wide")
st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग")

# आपकी नई Google Sheet "मिश्रा मार्केट डेटाबेस" का लिंक
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# डेटा लोड करने का फंक्शन
@st.cache_data(ttl=10) # डेटा को ताज़ा रखने के लिए
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        # अगर कॉलम के नाम में स्पेस हो तो उसे हटाना
        df.columns = df.columns.str.strip()
        # खाली दुकान वाले रो हटाना
        if 'Shop_Name' in df.columns:
            df = df.dropna(subset=['Shop_Name'])
        return df
    except Exception as e:
        st.error(f"शीट से डेटा नहीं मिल रहा: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    tab1, tab2 = st.tabs(["📊 बिलिंग डैशबोर्ड", "⚙️ मैनेजमेंट"])

    with tab1:
        st.subheader("दुकान चुनें और बिल देखें")
        
        # कॉलम चेक करना
        if 'Shop_Name' in df.columns:
            shop_list = df['Shop_Name'].unique().tolist()
            selected_shop = st.selectbox("दुकान का नाम चुनें:", shop_list)

            # चुनी हुई दुकान का डेटा
            shop_data = df[df['Shop_Name'] == selected_shop].iloc[0]

            # डेटा दिखाना
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📍 दुकान: {shop_data.get('Shop_Name', 'N/A')}")
                st.write(f"📱 WhatsApp: {shop_data.get('WhatsApp No', 'N/A')}")
                st.write(f"📉 पिछली रीडिंग: {shop_data.get('Prev_Reading', 0)}")
                st.write(f"📈 वर्तमान रीडिंग: {shop_data.get('Curr_Reading', 0)}")

            with col2:
                total = shop_data.get('Total_Amount', 0)
                st.metric("कुल बकाया राशि", f"₹{total}")
                st.write(f"⚡ यूनिट्स: {shop_data.get('Units_Used', 0)}")
                st.write(f"💰 फिक्स चार्ज: ₹{shop_data.get('Fix_Charge', 0)}")
                st.warning(f"स्थिति: {shop_data.get('Status', 'Pending')}")

            # WhatsApp भेजने का बटन (Optional)
            if st.button("WhatsApp पर बिल भेजें"):
                msg = f"नमस्ते {selected_shop}, आपका इस महीने का बिजली बिल ₹{total} है। कृपया समय पर भुगतान करें।"
                phone = str(shop_data.get('WhatsApp No', '')).replace('.0','')
                wa_link = f"https://wa.me/{phone}?text={msg}"
                st.markdown(f"[📲 यहाँ क्लिक करें]({wa_link})")
        else:
            st.error("शीट में 'Shop_Name' कॉलम नहीं मिला। कृपया कॉलम का नाम चेक करें।")

    with tab2:
        st.subheader("पूरी डेटाबेस लिस्ट")
        st.dataframe(df)

else:
    st.warning("शीट में अभी कोई डेटा नहीं मिला।")

st.sidebar.success("✅ डेटाबेस कनेक्टेड!")
