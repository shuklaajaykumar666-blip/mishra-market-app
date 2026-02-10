import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

st.set_page_config(page_title="मिश्रा मार्केट", layout="wide")

# डेटा लिंक
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        # सिर्फ कॉलम के नाम से स्पेस साफ़ करना ताकि कोड उन्हें ढूंढ सके
        df.columns = df.columns.str.strip()
        return df.dropna(subset=['Shop_Name'])
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("👑 मिश्रा मार्केट - लाइव बिलिंग")
    
    tab1, tab2 = st.tabs(["📊 डैशबोर्ड", "🧾 व्हाट्सएप बिल"])

    with tab1:
        # यहाँ हम सीधे आपके द्वारा दिए गए कॉलम के नाम इस्तेमाल कर रहे हैं
        c1, c2, c3 = st.columns(3)
        
        # शीट से सीधा डेटा उठाना (बिना किसी बदलाव के)
        # हमने pd.to_numeric सिर्फ इसलिए लगाया है ताकि 'Sum' (जोड़) हो सके
        total_collection = pd.to_numeric(df['Total_Amount'], errors='coerce').sum()
        total_units = pd.to_numeric(df['Units_Used'], errors='coerce').sum()
        
        c1.metric("कुल वसूली (Total Amount)", f"₹{total_collection:,.2f}")
        c2.metric("कुल दुकानें", len(df))
        c3.metric("कुल खपत (Units)", f"{total_units:,.0f}")

        st.divider()
        # ग्राफ भी अब सीधे 'Total_Amount' कॉलम से बनेगा
        fig = px.bar(df, x='Shop_Name', y='Total_Amount', color='Total_Amount', 
                     title="दुकान वार फाइनल बिल स्थिति")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    with tab2:
        st.subheader("दुकानदार का बिल चुनें")
        shop = st.selectbox("नाम चुनें:", df['Shop_Name'].unique())
        row = df[df['Shop_Name'] == shop].iloc[0]

        col_l, col_r = st.columns(2)
        with col_l:
            st.info(f"📍 दुकान: {shop}")
            st.write(f"📉 पिछली रीडिंग: {row['Prev_Reading']}")
            st.write(f"📈 नई रीडिंग: {row['Curr_Reading']}")
            st.write(f"🔢 इस्तेमाल यूनिट: {row['Units_Used']}")
        with col_r:
            st.success(f"💵 इस माह का बिल: ₹{row['Current_Bill']}")
            st.error(f"⚠️ पुराना बकाया: ₹{row['Pending_Balance']}")
            # यहाँ सीधा आपकी शीट का 'Total_Amount' दिखेगा
            st.warning(f"🏦 कुल देय राशि (Final): ₹{row['Total_Amount']}")

        # व्हाट्सएप संदेश - सीधे आपकी शीट की वैल्यूज के साथ
        msg = (
            f"👑 *मिश्रा मार्केट - बिजली बिल*\n\n"
            f"📍 दुकान: *{shop}*\n"
            f"🔢 यूनिट्स: {row['Units_Used']}\n"
            f"--------------------------\n"
            f"💵 माह बिल: ₹{row['Current_Bill']}\n"
            f"⚠️ बकाया: ₹{row['Pending_Balance']}\n"
            f"💰 *कुल जमा राशि: ₹{row['Total_Amount']}*\n"
            f"--------------------------\n"
            f"कृपया समय पर भुगतान करें। धन्यवाद। 🙏"
        )
        
        # फोन नंबर साफ़ करना
        phone = str(row['WhatsApp_No']).split('.')[0].replace(' ', '').replace('+', '')
        wa_url = f"https://wa.me/91{phone}?text={urllib.parse.quote(msg)}"
        
        st.divider()
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366;color:white;padding:15px;border:none;border-radius:10px;width:100%;font-weight:bold;cursor:pointer;font-size:18px;">🟢 व्हाट्सएप पर बिल भेजें</button></a>', unsafe_allow_html=True)

else:
    st.warning("डेटा लोड नहीं हो पाया।")
