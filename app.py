import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

st.set_page_config(page_title="मिश्रा मार्केट", layout="wide")

SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        # कॉलम के नाम से स्पेस हटाकर अंडरस्कोर लगाना
        df.columns = df.columns.str.strip().str.replace(' ', '_')
        
        if 'Shop_Name' in df.columns:
            df = df.dropna(subset=['Shop_Name'])
            # सभी जरूरी कॉलम्स को नंबर में बदलना
            cols_to_fix = ['Current_Bill', 'Pending_Balance', 'Total_Amount', 'Units_Used', 'Prev_Reading', 'Curr_Reading']
            for c in cols_to_fix:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                else:
                    df[c] = 0 # अगर कॉलम न मिले तो 0 मान लें
            return df
        return pd.DataFrame()
    except Exception as e:
        return str(e)

df = load_data()

if isinstance(df, pd.DataFrame) and not df.empty:
    st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग")
    
    tab1, tab2 = st.tabs(["📊 डैशबोर्ड", "🧾 व्हाट्सएप बिल भेजें"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        # यहाँ हम सीधे 'Total_Amount' का जोड़ दिखा रहे हैं
        final_collection = df['Total_Amount'].sum()
        
        c1.metric("कुल वसूली राशि (Total)", f"₹{final_collection:,.2f}")
        c2.metric("कुल दुकानें", len(df))
        c3.metric("कुल यूनिट्स", int(df['Units_Used'].sum()))

        st.divider()
        fig = px.bar(df, x='Shop_Name', y='Total_Amount', color='Total_Amount', 
                     title="दुकान वार कुल देय राशि (बकाया + करंट)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    with tab2:
        st.subheader("दुकानदार का बिल")
        shop = st.selectbox("नाम चुनें:", df['Shop_Name'].unique())
        row = df[df['Shop_Name'] == shop].iloc[0]

        # --- यहाँ है असली बदलाव ---
        curr = row['Current_Bill']
        pend = row['Pending_Balance']
        total_payable = row['Total_Amount'] # सीधे आपकी शीट का फाइनल कॉलम

        col_l, col_r = st.columns(2)
        with col_l:
            st.info(f"📍 दुकान: {shop}")
            st.write(f"📉 पिछली रीडिंग: {row['Prev_Reading']}")
            st.write(f"📈 नई रीडिंग: {row['Curr_Reading']}")
            st.write(f"⚡ कुल यूनिट: {row['Units_Used']}")
        with col_r:
            st.success(f"💵 इस महीने का बिल: ₹{curr}")
            st.error(f"⚠️ पुराना बकाया: ₹{pend}")
            # यहाँ अब वही दिखेगा जो आपकी शीट में 'Total_Amount' के नीचे है
            st.warning(f"🏦 कुल देय राशि (Final): ₹{total_payable}")

        # व्हाट्सएप संदेश में भी 'Total_Amount' इस्तेमाल होगा
        msg = (
            f"👑 *मिश्रा मार्केट - बिजली बिल*\n\n"
            f"📍 दुकान: *{shop}*\n"
            f"🔢 यूनिट्स: {row['Units_Used']}\n"
            f"--------------------------\n"
            f"💵 माह बिल: ₹{curr}\n"
            f"⚠️ बकाया: ₹{pend}\n"
            f"💰 *कुल जमा राशि: ₹{total_payable}*\n"
            f"--------------------------\n"
            f"कृपया समय पर भुगतान करें। धन्यवाद। 🙏"
        )
        
        phone = str(row.get('WhatsApp_No', '')).split('.')[0].replace(' ', '')
        wa_url = f"https://wa.me/91{phone}?text={urllib.parse.quote(msg)}"
        
        st.divider()
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366;color:white;padding:15px;border:none;border-radius:10px;width:100%;font-weight:bold;cursor:pointer;">🟢 व्हाट्सएप पर फाइनल बिल भेजें</button></a>', unsafe_allow_html=True)

else:
    st.error("डेटा लोड नहीं हो पाया।")
