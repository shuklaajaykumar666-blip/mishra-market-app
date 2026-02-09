import streamlit as st
import pandas as pd

# --- पेज की सेटिंग ---
st.set_page_config(page_title="मिश्रा मार्केट बिलिंग", layout="wide")
st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग सिस्टम")

# आपकी गूगल शीट की जानकारी
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
GID = "1626084043"  # SHOP_DATA टैब का ID
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

def load_data():
    try:
        # शीट से डेटा उठाना
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip() # फालतू स्पेस हटाना
        # खाली लाइनें हटाना
        df = df.dropna(subset=['Shop_Name'])
        return df
    except Exception as e:
        st.error(f"डेटा लोड करने में समस्या: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- मुख्य डैशबोर्ड ---
    tab1, tab2 = st.tabs(["📊 बिल देखें", "📋 पूरी लिस्ट"])

    with tab1:
        st.subheader("दुकानदार का नाम चुनें")
        shop_list = df['Shop_Name'].unique().tolist()
        selected_shop = st.selectbox("", shop_list)

        # चुनी हुई दुकान का डेटा निकालना
        data = df[df['Shop_Name'] == selected_shop].iloc[0]

        # तीन डिब्बों (Cards) में मुख्य जानकारी
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("इस महीने का बिल", f"₹{data.get('Current_Bill', 0)}")
        with col2:
            st.metric("खर्च हुई यूनिट", f"{data.get('Units_Used', 0)}")
        with col3:
            st.metric("पुराना बकाया", f"₹{data.get('Pending_Balance', 0)}")

        st.divider()

        # बाकी जानकारी दो कॉलम में
        left, right = st.columns(2)
        with left:
            st.info(f"📱 व्हाट्सएप नंबर: {data.get('WhatsApp_No', 'N/A')}")
            st.write(f"📉 पिछली रीडिंग: {data.get('Prev_Reading', 0)}")
            st.write(f"📈 नई रीडिंग: {data.get('Curr_Reading', 0)}")
        
        with right:
            st.success(f"💰 कुल जमा राशि: ₹{data.get('Paid_Amt', 0)}")
            st.write(f"📅 पेमेंट की तारीख: {data.get('Pay_Date', 'N/A')}")
            st.write(f"⚡ यूनिट रेट: ₹{data.get('Effective_Unit_Rate', 0)}")

    with tab2:
        st.subheader("मार्केट के सभी दुकानों का डेटा")
        # सिर्फ जरूरी कॉलम दिखाना
        st.dataframe(df[['Shop_Name', 'WhatsApp_No', 'Units_Used', 'Current_Bill', 'Pending_Balance']])

else:
    st.warning("शीट में कोई डेटा नहीं मिला। कृपया अपनी गूगल शीट चेक करें।")

# साइडबार में स्टेटस
st.sidebar.markdown("---")
st.sidebar.success("✅ डेटाबेस से जुड़ा हुआ है")
st.sidebar.info("मिश्रा मार्केट, बलिया")
