import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

st.set_page_config(page_title="मिश्रा मार्केट - मैनेजमेंट", layout="wide")

# डेटा लिंक
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"

# डेटा लोड करने का सबसे सुरक्षित तरीका
def load_sheet(gid):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
        df = pd.read_csv(url)
        # कॉलम के नाम से सिर्फ फालतू स्पेस हटाना, नाम वही रहेंगे जो आपने दिए हैं
        df.columns = df.columns.str.strip()
        # नंबर वाले कॉलम को साफ़ करना
        for col in df.columns:
            if any(x in col for x in ['Amount', 'Bill', 'Reading', 'Units', 'Charge', 'Balance', 'Payable', 'Paid']):
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame()

# टैब के हिसाब से GID लोड करना (कृपया अपनी शीट से GID चेक कर लें, SHOP_DATA=1626084043)
df_shop = load_sheet("1626084043")
df_ledger = load_sheet("0") # PAYMENT_LEDGER का GID यहाँ डालें
df_govt = load_sheet("123456789") # GOVT_BILL_DATA का GID यहाँ डालें

if not df_shop.empty:
    st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग सिस्टम")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 डैशबोर्ड", "🧾 व्हाट्सएप बिल", "💰 पेमेंट लेजर", "⚡ सरकारी हिसाब"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        # आपके दिए कॉलम 'Total_Payable_Amount' का इस्तेमाल
        total_to_collect = df_shop['Total_Payable_Amount'].sum()
        c1.metric("कुल वसूली (Total Payable)", f"₹{total_to_collect:,.2f}")
        c2.metric("कुल दुकानें", len(df_shop))
        c3.metric("कुल खपत (Units)", f"{df_shop['Units'].sum():,.0f}")
        
        st.divider()
        fig = px.bar(df_shop, x='Shop_Name', y='Total_Payable_Amount', color='Total_Payable_Amount', title="दुकान वार कुल देय राशि")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_shop)

    with tab2:
        st.subheader("दुकानदार का बिल भेजें")
        selected_shop = st.selectbox("नाम चुनें:", df_shop['Shop_Name'].unique())
        row = df_shop[df_shop['Shop_Name'] == selected_shop].iloc[0]

        col_l, col_r = st.columns(2)
        with col_l:
            st.info(f"📍 दुकान: {selected_shop}")
            st.write(f"📱 व्हाट्सएप: {row['WhatsApp_No']}")
            st.write(f"📉 रीडिंग: {row['Prev_Reading']} से {row['Current_Reading']}")
            st.write(f"⚡ यूनिट्स: {row['Units']}")
        with col_r:
            st.success(f"💵 इस महीने का बिल: ₹{row['Current_Bill']}")
            st.error(f"⚠️ पुराना बकाया: ₹{row['Pending_Amount']}")
            st.warning(f"🏦 कुल देय राशि: ₹{row['Total_Payable_Amount']}")

        # व्हाट्सएप संदेश - आपके सटीक कॉलम नामों के साथ
        message = (
            f"👑 *मिश्रा मार्केट - बिजली बिल*\n"
            f"📅 महीना: {row['Month']} {row['Year']}\n"
            f"--------------------------\n"
            f"📍 दुकान: *{selected_shop}*\n"
            f"🔢 यूनिट्स: {row['Units']}\n"
            f"--------------------------\n"
            f"💵 माह बिल: ₹{row['Current_Bill']}\n"
            f"⚠️ पुराना बकाया: ₹{row['Pending_Amount']}\n"
            f"💰 *कुल जमा राशि: ₹{row['Total_Payable_Amount']}*\n"
            f"📅 अंतिम तिथि: {row['Payment_Due_Date']}\n"
            f"--------------------------\n"
            f"धन्यवाद। 🙏"
        )
        
        phone = str(row['WhatsApp_No']).split('.')[0].replace(' ', '').replace('+', '')
        wa_url = f"https://wa.me/91{phone}?text={urllib.parse.quote(message)}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366;color:white;padding:15px;border:none;border-radius:10px;width:100%;font-weight:bold;cursor:pointer;width:100%;">🟢 व्हाट्सएप पर बिल भेजें</button></a>', unsafe_allow_html=True)

    with tab3:
        st.subheader("💰 पेमेंट लेजर रिकॉर्ड")
        if not df_ledger.empty:
            st.dataframe(df_ledger, use_container_width=True)
        else:
            st.info("पेमेंट लेजर का डेटा लोड करें।")

    with tab4:
        st.subheader("⚡ सरकारी बिल तुलना")
        if not df_govt.empty:
            st.dataframe(df_govt, use_container_width=True)
        else:
            st.info("सरकारी बिल डेटा लोड करें।")

else:
    st.error("डेटा लोड नहीं हो पाया। SHOP_DATA को अपनी शीट में पहले नंबर पर रखें।")
