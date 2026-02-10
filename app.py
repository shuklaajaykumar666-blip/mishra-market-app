import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

st.set_page_config(page_title="मिश्रा मार्केट - बिलिंग", layout="wide")

# डेटा लिंक
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"

# अलग-अलग टैब के लिए फंक्शन
@st.cache_data(ttl=10)
def load_data(gid="0"):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.replace(' ', '_')
        return df
    except:
        return pd.DataFrame()

# मुख्य SHOP_DATA लोड करना (GID: 1626084043)
df = load_data("1626084043")

if not df.empty:
    st.title("👑 मिश्रा मार्केट - स्मार्ट डैशबोर्ड")
    
    # --- मेन्यू टैब्स ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 डैशबोर्ड", "🧾 व्हाट्सएप बिल", "💰 पेमेंट लेजर", "⚡ सरकारी हिस्ट्री"])

    with tab1:
        # यहाँ हमने 'Total_Amount' का इस्तेमाल किया है (Current + Pending)
        # अगर आपके कॉलम का नाम अलग है तो कोड इसे संभाल लेगा
        total_col = 'Total_Amount' if 'Total_Amount' in df.columns else 'Current_Bill'
        
        c1, c2, c3 = st.columns(3)
        total_to_collect = pd.to_numeric(df[total_col], errors='coerce').sum()
        c1.metric("कुल वसूली (Total Collection)", f"₹{total_to_collect:,.2f}")
        c2.metric("कुल दुकानें", len(df))
        c3.metric("कुल बकाया", f"₹{pd.to_numeric(df.get('Pending_Balance', 0), errors='coerce').sum():,.2f}")
        
        st.divider()
        fig = px.bar(df, x='Shop_Name', y=total_col, color=total_col, title="दुकान वार कुल देय राशि (Total Payable)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    with tab2:
        st.subheader("दुकानदार का बिल तैयार करें")
        selected_shop = st.selectbox("नाम चुनें:", df['Shop_Name'].unique())
        row = df[df['Shop_Name'] == selected_shop].iloc[0]

        # गणना: Current + Pending = Total
        curr = pd.to_numeric(row.get('Current_Bill', 0), errors='coerce')
        pend = pd.to_numeric(row.get('Pending_Balance', 0), errors='coerce')
        # अगर आपकी शीट में 'Total_Amount' कॉलम है तो वो उठाएगा, वरना कैलकुलेट करेगा
        final_total = row.get('Total_Amount', curr + pend)

        col_l, col_r = st.columns(2)
        with col_l:
            st.info(f"📍 दुकान: {selected_shop}")
            st.write(f"📉 पिछली रीडिंग: {row.get('Prev_Reading', 0)}")
            st.write(f"📈 नई रीडिंग: {row.get('Curr_Reading', 0)}")
            st.write(f"⚡ यूनिट्स: {row.get('Units_Used', 0)}")
        with col_r:
            st.success(f"💵 इस महीने का बिल: ₹{curr}")
            st.error(f"⚠️ पुराना बकाया: ₹{pend}")
            st.warning(f"🏦 कुल देय राशि (Total Payable): ₹{final_total}")

        # व्हाट्सएप मैसेज
        message = (
            f"👑 *मिश्रा मार्केट - बिजली बिल*\n\n"
            f"📍 दुकान: *{selected_shop}*\n"
            f"🔢 यूनिट्स: {row.get('Units_Used', 0)}\n"
            f"--------------------------\n"
            f"💵 इस माह का बिल: ₹{curr}\n"
            f"⚠️ पुराना बकाया: ₹{pend}\n"
            f"💰 *कुल जमा करने वाली राशि: ₹{final_total}*\n"
            f"--------------------------\n"
            f"कृपया भुगतान समय पर करें। धन्यवाद। 🙏"
        )
        
        encoded_msg = urllib.parse.quote(message)
        phone = str(row.get('WhatsApp_No', '')).split('.')[0]
        wa_url = f"https://wa.me/91{phone}?text={encoded_msg}"

        st.divider()
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366;color:white;padding:15px;border:none;border-radius:10px;width:100%;font-weight:bold;cursor:pointer;">🟢 व्हाट्सएप पर फाइनल बिल भेजें</button></a>', unsafe_allow_html=True)

    with tab3:
        st.subheader("💰 पेमेंट लेजर (History)")
        # यहाँ हम Sheet1 (GID: 0) लोड कर रहे हैं, आप अपनी शीट का GID बदल सकते हैं
        df_ledger = load_data("0") 
        if not df_ledger.empty:
            st.dataframe(df_ledger, use_container_width=True)
        else:
            st.info("लेजर डेटा लोड करने के लिए कृपया GID चेक करें।")

    with tab4:
        st.subheader("⚡ सरकारी मीटर हिस्ट्री")
        # सरकारी हिस्ट्री के लिए जो भी आपका GID हो वो यहाँ डालें
        df_gov = load_data("123456789") # उदाहरण GID
        if not df_gov.empty:
            st.dataframe(df_gov, use_container_width=True)
        else:
            st.info("सरकारी हिस्ट्री का GID यहाँ अपडेट करें।")

else:
    st.error("डेटा लोड नहीं हो पाया।")
