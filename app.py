import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

st.set_page_config(page_title="मिश्रा मार्केट मैनेजमेंट", layout="wide")

# डेटा लिंक (बिना GID के, ताकि यह पूरी फाइल को एक्सेस कर सके)
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"

@st.cache_data(ttl=5)
def load_all_data():
    try:
        # यहाँ हम सीधे CSV एक्सपोर्ट का उपयोग कर रहे हैं जो पहले टैब को उठाता है
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip() # सिर्फ स्पेस साफ़ करना
        return df
    except Exception as e:
        return pd.DataFrame()

df_shop = load_all_data()

if not df_shop.empty:
    st.title("👑 मिश्रा मार्केट - स्मार्ट मैनेजमेंट")
    
    tab1, tab2, tab3 = st.tabs(["📊 डैशबोर्ड", "🧾 व्हाट्सएप बिल", "💰 अन्य रिकॉर्ड"])

    with tab1:
        # आपके कॉलम नामों का उपयोग: Total_Payable_Amount
        c1, c2, c3 = st.columns(3)
        
        # सुरक्षित तरीके से नंबर में बदलना ताकि एरर न आए
        total_amt = pd.to_numeric(df_shop['Total_Payable_Amount'], errors='coerce').sum()
        total_units = pd.to_numeric(df_shop['Units'], errors='coerce').sum()
        
        c1.metric("कुल वसूली (Total Payable)", f"₹{total_amt:,.2f}")
        c2.metric("कुल दुकानें", len(df_shop))
        c3.metric("कुल यूनिट्स", f"{int(total_units)}")
        
        st.divider()
        fig = px.bar(df_shop, x='Shop_Name', y='Total_Payable_Amount', color='Total_Payable_Amount', title="दुकान वार कुल बिल")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_shop)

    with tab2:
        st.subheader("दुकानदार का बिल भेजें")
        selected_shop = st.selectbox("नाम चुनें:", df_shop['Shop_Name'].unique())
        row = df_shop[df_shop['Shop_Name'] == selected_shop].iloc[0]

        col_l, col_r = st.columns(2)
        with col_l:
            st.info(f"📍 दुकान: {selected_shop}")
            st.write(f"📉 रीडिंग: {row['Prev_Reading']} -> {row['Current_Reading']}")
            st.write(f"🔢 यूनिट्स: {row['Units']}")
            st.write(f"📅 देय तिथि: {row['Payment_Due_Date']}")
        with col_r:
            st.success(f"💵 माह बिल: ₹{row['Current_Bill']}")
            st.error(f"⚠️ बकाया: ₹{row['Pending_Amount']}")
            st.warning(f"🏦 कुल देय राशि: ₹{row['Total_Payable_Amount']}")

        # व्हाट्सएप मैसेज - आपके सटीक कॉलम नामों के साथ
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
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366;color:white;padding:15px;border:none;border-radius:10px;width:100%;font-weight:bold;cursor:pointer;width:100%;">🟢 व्हाट्सएप पर फाइनल बिल भेजें</button></a>', unsafe_allow_html=True)

    with tab3:
        st.info("💡 PAYMENT_LEDGER और GOVT_BILL_DATA देखने के लिए सुनिश्चित करें कि वे आपकी गूगल शीट के अन्य टैब में मौजूद हैं।")
        st.write("अभी आप मुख्य डैशबोर्ड और व्हाट्सएप बिल का उपयोग कर सकते हैं।")

else:
    st.error("डेटा लोड नहीं हो पाया।")
    st.info("💡 समाधान: अपनी गूगल शीट खोलें और नीचे 'SHOP_DATA' वाले टैब को माउस से पकड़कर सबसे बाईं (पहले) नंबर पर खिसका दें।")
