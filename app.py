import streamlit as st
import pandas as pd
import plotly.express as px

# --- पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="मिश्रा मार्केट डैशबोर्ड", layout="wide")
st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग एवं लेजर")

# शीट की जानकारी
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"

# अलग-अलग टैब के GIDs (आपकी शीट के हिसाब से)
GID_SHOP = "1626084043"    # SHOP_DATA
GID_LEDGER = "0"           # Payment Ledger (अगर Sheet1 है तो 0, वरना अपनी GID चेक करें)
GID_GOV = "123456789"      # Gov History (उदाहरण के लिए, अपनी GID यहाँ डालें)

@st.cache_data(ttl=600)
def load_sheet_data(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df.fillna(0)
    except:
        return pd.DataFrame()

# डेटा लोड करना
df_shop = load_sheet_data(GID_SHOP)

# --- मुख्य डैशबोर्ड लेआउट ---
menu = ["📊 मुख्य डैशबोर्ड", "📑 दुकान बिल एवं लेजर", "⚡ सरकारी मीटर हिस्ट्री", "💰 कुल पेमेंट लेजर"]
choice = st.sidebar.selectbox("मेन्यू चुनें", menu)

if not df_shop.empty:
    
    if choice == "📊 मुख्य डैशबोर्ड":
        st.subheader("मार्केट की स्थिति (Overview)")
        
        # टॉप कार्ड्स
        t1, t2, t3 = st.columns(3)
        with t1:
            total_bill = df_shop['Current_Bill'].sum()
            st.metric("कुल मासिक बिल", f"₹{total_bill:,.2f}")
        with t2:
            total_pending = df_shop['Pending_Balance'].sum()
            st.metric("कुल बकाया", f"₹{total_pending:,.2f}", delta_color="inverse")
        with t3:
            total_shops = len(df_shop)
            st.metric("कुल दुकानें", total_shops)

        st.divider()

        # चार्ट्स
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 📈 दुकान वार बिल")
            fig = px.bar(df_shop, x='Shop_Name', y='Current_Bill', color='Current_Bill', 
                         labels={'Current_Bill':'बिल', 'Shop_Name':'दुकान'})
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown("### 🥧 बकाया राशि का वितरण")
            fig2 = px.pie(df_shop, values='Pending_Balance', names='Shop_Name', hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)

    elif choice == "📑 दुकान बिल एवं लेजर":
        st.subheader("व्यक्तिगत दुकान की जानकारी")
        shop = st.selectbox("दुकान चुनें", df_shop['Shop_Name'].unique())
        s_data = df_shop[df_shop['Shop_Name'] == shop].iloc[0]
        
        col_l, col_r = st.columns(2)
        with col_l:
            st.info(f"📍 दुकान: {shop}")
            st.write(f"📱 संपर्क: {s_data.get('WhatsApp_No', 'N/A')}")
            st.write(f"📉 पिछली रीडिंग: {s_data.get('Prev_Reading', 0)}")
            st.write(f"📈 नई रीडिंग: {s_data.get('Curr_Reading', 0)}")
        
        with col_r:
            st.success(f"💵 इस महीने का बिल: ₹{s_data.get('Current_Bill', 0)}")
            st.error(f"⚠️ बकाया: ₹{s_data.get('Pending_Balance', 0)}")
            st.warning(f"🏦 कुल देय राशि: ₹{float(s_data.get('Current_Bill',0)) + float(s_data.get('Pending_Balance',0))}")

    elif choice == "⚡ सरकारी मीटर हिस्ट्री":
        st.subheader("सरकारी मीटर (Main Meter) का रिकॉर्ड")
        # यहाँ आप सरकारी मीटर वाले टैब का डेटा दिखा सकते हैं
        st.info("सरकारी मीटर टैब से डेटा यहाँ लोड किया जा रहा है...")
        st.dataframe(df_shop[df_shop['Shop_Name'] == 'Sarkari Meter']) # उदाहरण

    elif choice == "💰 कुल पेमेंट लेजर":
        st.subheader("मार्केट पेमेंट लेजर")
        st.dataframe(df_shop[['Shop_Name', 'Paid_Amt', 'Pay_Date', 'Status']])

else:
    st.error("डेटा लोड नहीं हो पाया! कृपया पक्का करें कि शीट में डेटा सही है।")

st.sidebar.markdown("---")
st.sidebar.write("अंतिम अपडेट: 2026")
