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
        # कॉलम के नाम से स्पेस हटाना
        df.columns = df.columns.str.strip()
        
        if 'Shop_Name' in df.columns:
            df = df.dropna(subset=['Shop_Name'])
            
            # --- कॉलम डिटेक्टर ---
            # हम ढूंढ रहे हैं कि 'Total_Amount' वाला कॉलम असली में किस नाम से है
            potential_names = ['Total_Amount', 'Total Amount', 'Total_Payable_Amount', 'Total_Payable', 'Total']
            actual_total_col = None
            
            for name in potential_names:
                if name in df.columns:
                    actual_total_col = name
                    break
            
            # अगर मिल गया, तो उसे एक मानक नाम 'Final_Total' दे दो
            if actual_total_col:
                df['Final_Total'] = pd.to_numeric(df[actual_total_col], errors='coerce').fillna(0)
            else:
                # अगर कोई भी नाम मैच नहीं हुआ, तो खुद जोड़ लो (Safety Net)
                curr = pd.to_numeric(df.get('Current_Bill', 0), errors='coerce').fillna(0)
                pend = pd.to_numeric(df.get('Pending_Balance', 0), errors='coerce').fillna(0)
                df['Final_Total'] = curr + pend

            # बाकी जरूरी कॉलम्स को भी नंबर में बदलें
            for c in ['Current_Bill', 'Pending_Balance', 'Units_Used']:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            
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
        total_sum = df['Final_Total'].sum()
        
        c1.metric("कुल वसूली राशि", f"₹{total_sum:,.2f}")
        c2.metric("कुल दुकानें", len(df))
        c3.metric("कुल यूनिट्स", int(df.get('Units_Used', 0).sum()))

        st.divider()
        fig = px.bar(df, x='Shop_Name', y='Final_Total', color='Final_Total', title="दुकान वार कुल बिल")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    with tab2:
        st.subheader("दुकानदार का बिल")
        shop = st.selectbox("नाम चुनें:", df['Shop_Name'].unique())
        row = df[df['Shop_Name'] == shop].iloc[0]

        curr_bill = row.get('Current_Bill', 0)
        pend_bill = row.get('Pending_Balance', 0)
        final_amt = row['Final_Total'] # यहाँ अब सही वैल्यू आएगी

        col_l, col_r = st.columns(2)
        with col_l:
            st.info(f"📍 दुकान: {shop}")
            st.write(f"📉 पिछली रीडिंग: {row.get('Prev_Reading', 0)}")
            st.write(f"📈 नई रीडिंग: {row.get('Curr_Reading', 0)}")
        with col_r:
            st.success(f"💵 इस महीने का बिल: ₹{curr_bill}")
            st.error(f"⚠️ पुराना बकाया: ₹{pend_bill}")
            st.warning(f"🏦 कुल देय राशि (Final): ₹{final_amt}")

        # व्हाट्सएप संदेश
        msg = (
            f"👑 *मिश्रा मार्केट - बिजली बिल*\n\n"
            f"📍 दुकान: *{shop}*\n"
            f"--------------------------\n"
            f"💵 माह बिल: ₹{curr_bill}\n"
            f"⚠️ बकाया: ₹{pend_bill}\n"
            f"💰 *कुल जमा राशि: ₹{final_amt}*\n"
            f"--------------------------\n"
            f"धन्यवाद। 🙏"
        )
        
        phone = str(row.get('WhatsApp_No', '')).split('.')[0].replace(' ', '')
        wa_url = f"https://wa.me/91{phone}?text={urllib.parse.quote(msg)}"
        
        st.divider()
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366;color:white;padding:15px;border:none;border-radius:10px;width:100%;font-weight:bold;cursor:pointer;">🟢 व्हाट्सएप पर फाइनल बिल भेजें</button></a>', unsafe_allow_html=True)

else:
    st.error("डेटा लोड नहीं हो पाया।")
