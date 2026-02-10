import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

st.set_page_config(page_title="मिश्रा मार्केट", layout="wide")

# आपका पक्का लिंक
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip()
        # नंबर वाले कॉलम्स को साफ़ करना ताकि व्हाट्सएप पर सही वैल्यू जाए
        num_cols = ['Current_Bill', 'Units_Used', 'Pending_Balance', 'Prev_Reading', 'Curr_Reading']
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df.dropna(subset=['Shop_Name'])
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग")
    
    # --- मेन्यू ---
    tab1, tab2 = st.tabs(["📊 डैशबोर्ड", "🧾 व्हाट्सएप बिल भेजें"])

    with tab1:
        c1, c2 = st.columns(2)
        total_bill = df['Current_Bill'].sum()
        c1.metric("कुल मार्केट बिल", f"₹{total_bill:,.2f}")
        c2.metric("कुल दुकानें", len(df))
        
        st.divider()
        fig = px.bar(df, x='Shop_Name', y='Current_Bill', color='Current_Bill', title="दुकान वार बिल")
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("📋 पूरी लिस्ट")
        st.dataframe(df)

    with tab2:
        st.subheader("दुकानदार चुनें")
        selected_shop = st.selectbox("नाम चुनें:", df['Shop_Name'].unique())
        row = df[df['Shop_Name'] == selected_shop].iloc[0]

        # रसीद की तरह डेटा दिखाना
        col_l, col_r = st.columns(2)
        with col_l:
            st.write(f"📱 व्हाट्सएप: {row.get('WhatsApp_No', 'N/A')}")
            st.write(f"📉 पुरानी रीडिंग: {row.get('Prev_Reading', 0)}")
            st.write(f"📈 नई रीडिंग: {row.get('Curr_Reading', 0)}")
        with col_r:
            st.success(f"💵 इस महीने का बिल: ₹{row['Current_Bill']}")
            st.error(f"⚠️ बकाया: ₹{row['Pending_Balance']}")
            total_amount = row['Current_Bill'] + row['Pending_Balance']
            st.warning(f"🏦 कुल देय राशि: ₹{total_amount}")

        # --- व्हाट्सएप बटन का जादू ---
        # मैसेज का फॉर्मेट
        message = (
            f"👑 *मिश्रा मार्केट - बिजली बिल*\n\n"
            f"📍 दुकान: *{selected_shop}*\n"
            f"🔢 यूनिट्स: {row['Units_Used']}\n"
            f"📊 नई रीडिंग: {row['Curr_Reading']}\n"
            f"--------------------------\n"
            f"💵 इस माह का बिल: ₹{row['Current_Bill']}\n"
            f"⚠️ पुराना बकाया: ₹{row['Pending_Balance']}\n"
            f"💰 *कुल जमा राशि: ₹{total_amount}*\n"
            f"--------------------------\n"
            f"कृपया समय पर भुगतान करें। धन्यवाद। 🙏"
        )
        
        encoded_msg = urllib.parse.quote(message)
        # नंबर में अगर 91 नहीं है तो जोड़ देगा
        phone = str(row.get('WhatsApp_No', '')).split('.')[0] # पॉइंट हटाना अगर हो तो
        wa_url = f"https://wa.me/91{phone}?text={encoded_msg}"

        st.divider()
        st.markdown(f'''
            <a href="{wa_url}" target="_blank">
                <button style="background-color: #25D366; color: white; padding: 15px 32px; border: none; border-radius: 10px; cursor: pointer; font-size: 18px; font-weight: bold; width: 100%;">
                    🟢 व्हाट्सएप पर बिल भेजें
                </button>
            </a>
            ''', unsafe_allow_html=True)

else:
    st.error("डेटा लोड नहीं हो पाया।")

st.sidebar.success("वर्जन 3.0 एक्टिव है")
