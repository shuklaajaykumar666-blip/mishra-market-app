import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

st.set_page_config(page_title="मिश्रा मार्केट बिलिंग", layout="wide")

SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"

# डेटा लोड करने का सुरक्षित फंक्शन
def load_sheet_data(gid):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.replace(' ', '_')
        return df
    except:
        return pd.DataFrame()

# मुख्य डेटा (SHOP_DATA) को लोड करना
df = load_sheet_data("1626084043")

if not df.empty:
    st.title("👑 मिश्रा मार्केट - स्मार्ट डैशबोर्ड")
    
    # टैब बनाना
    tab1, tab2, tab3 = st.tabs(["📊 डैशबोर्ड", "🧾 व्हाट्सएप बिल", "📑 अन्य रिकॉर्ड"])

    with tab1:
        # टोटल बिल की गणना
        # हम पक्का कर रहे हैं कि 'Total_Amount' ही दिखे
        target_col = 'Total_Amount' if 'Total_Amount' in df.columns else 'Current_Bill'
        
        c1, c2, c3 = st.columns(3)
        total_val = pd.to_numeric(df[target_col], errors='coerce').sum()
        c1.metric("कुल वसूली राशि", f"₹{total_val:,.2f}")
        c2.metric("कुल दुकानें", len(df))
        c3.metric("कुल बकाया (Pending)", f"₹{pd.to_numeric(df.get('Pending_Balance', 0), errors='coerce').sum():,.2f}")
        
        st.divider()
        fig = px.bar(df, x='Shop_Name', y=target_col, color=target_col, title="दुकान वार कुल बिल (Current + Pending)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    with tab2:
        st.subheader("दुकानदार का बिल")
        selected_shop = st.selectbox("नाम चुनें:", df['Shop_Name'].unique())
        row = df[df['Shop_Name'] == selected_shop].iloc[0]

        # वैल्यू को साफ़ करना
        curr = pd.to_numeric(row.get('Current_Bill', 0), errors='coerce')
        pend = pd.to_numeric(row.get('Pending_Balance', 0), errors='coerce')
        # अगर Total_Amount कॉलम है तो वो, वरना दोनों का जोड़
        final_bill = row.get('Total_Amount', curr + pend)

        col_l, col_r = st.columns(2)
        with col_l:
            st.info(f"📍 दुकान: {selected_shop}")
            st.write(f"📉 पिछली रीडिंग: {row.get('Prev_Reading', 0)}")
            st.write(f"📈 नई रीडिंग: {row.get('Curr_Reading', 0)}")
        with col_r:
            st.success(f"💵 इस महीने का बिल: ₹{curr}")
            st.error(f"⚠️ पुराना बकाया: ₹{pend}")
            st.warning(f"🏦 कुल देय राशि: ₹{final_bill}")

        # व्हाट्सएप मैसेज फॉर्मेट
        message = (
            f"👑 *मिश्रा मार्केट - बिजली बिल*\n\n"
            f"📍 दुकान: *{selected_shop}*\n"
            f"--------------------------\n"
            f"💵 इस माह का बिल: ₹{curr}\n"
            f"⚠️ पुराना बकाया: ₹{pend}\n"
            f"💰 *कुल देय राशि: ₹{final_bill}*\n"
            f"--------------------------\n"
            f"कृपया भुगतान समय पर करें। धन्यवाद। 🙏"
        )
        
        encoded_msg = urllib.parse.quote(message)
        phone = str(row.get('WhatsApp_No', '')).split('.')[0]
        wa_url = f"https://wa.me/91{phone}?text={encoded_msg}"

        st.divider()
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366;color:white;padding:15px;border:none;border-radius:10px;width:100%;font-weight:bold;cursor:pointer;">🟢 व्हाट्सएप पर बिल भेजें</button></a>', unsafe_allow_html=True)

    with tab3:
        st.info("यहाँ आप अपनी शीट के अन्य टैब देख सकते हैं।")
        sub_tab1, sub_tab2 = st.tabs(["पेमेंट लेजर", "सरकारी हिस्ट्री"])
        with sub_tab1:
            # GID "0" आमतौर पर पहले टैब के लिए होता है
            ledger = load_sheet_data("0")
            st.dataframe(ledger)
        with sub_tab2:
            # यहाँ अपनी Gov History का पक्का GID डालिये
            gov = load_sheet_data("अपना_GID_यहाँ_डालें")
            st.dataframe(gov)

else:
    st.error("डेटा लोड नहीं हो पाया। कृपया पक्का करें कि SHOP_DATA टैब आपकी शीट में पहले नंबर पर है।")
