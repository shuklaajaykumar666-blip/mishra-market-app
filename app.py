import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

st.set_page_config(page_title="मिश्रा मार्केट", layout="wide")

# --- सबसे सुरक्षित लिंक तरीका ---
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
# बिना GID के यह सीधे पहले पन्ने को लोड करेगा
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        # सीधा CSV लोड करना
        df = pd.read_csv(CSV_URL)
        # कॉलम के नामों को साफ़ करना
        df.columns = df.columns.str.strip().str.replace(' ', '_')
        # अगर Shop_Name है तो ही आगे बढ़ना
        if 'Shop_Name' in df.columns:
            df = df.dropna(subset=['Shop_Name'])
            # नंबरों को सही करना
            for c in ['Current_Bill', 'Pending_Balance', 'Total_Amount', 'Units_Used']:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        return pd.DataFrame()
    except Exception as e:
        return str(e)

df = load_data()

if isinstance(df, pd.DataFrame) and not df.empty:
    st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग")
    
    # टैब सेटअप
    tab1, tab2 = st.tabs(["📊 डैशबोर्ड", "🧾 व्हाट्सएप बिल भेजें"])

    with tab1:
        # आंकड़ों का प्रदर्शन
        c1, c2, c3 = st.columns(3)
        # अगर Total_Amount कॉलम है तो वो, वरना Current+Pending
        total_to_collect = df['Total_Amount'].sum() if 'Total_Amount' in df.columns else (df['Current_Bill'] + df['Pending_Balance']).sum()
        
        c1.metric("कुल देय राशि (Total)", f"₹{total_to_collect:,.2f}")
        c2.metric("कुल दुकानें", len(df))
        c3.metric("कुल बिजली यूनिट", int(df['Units_Used'].sum()))

        st.divider()
        # ग्राफ - अब यह 'Total Amount' दिखाएगा
        y_val = 'Total_Amount' if 'Total_Amount' in df.columns else 'Current_Bill'
        fig = px.bar(df, x='Shop_Name', y=y_val, color=y_val, title="दुकान वार कुल बिल (बकाया सहित)")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 पूरी रिपोर्ट")
        st.dataframe(df)

    with tab2:
        st.subheader("दुकानदार का बिल")
        shop = st.selectbox("नाम चुनें:", df['Shop_Name'].unique())
        row = df[df['Shop_Name'] == shop].iloc[0]

        # गणना
        curr = row.get('Current_Bill', 0)
        pend = row.get('Pending_Balance', 0)
        total = row.get('Total_Amount', curr + pend)

        col_l, col_r = st.columns(2)
        with col_l:
            st.info(f"📍 दुकान: {shop}")
            st.write(f"📉 पिछली रीडिंग: {row.get('Prev_Reading', 0)}")
            st.write(f"📈 नई रीडिंग: {row.get('Curr_Reading', 0)}")
        with col_r:
            st.success(f"💵 इस महीने का बिल: ₹{curr}")
            st.error(f"⚠️ पुराना बकाया: ₹{pend}")
            st.warning(f"🏦 कुल जमा राशि: ₹{total}")

        # व्हाट्सएप संदेश
        msg = (
            f"👑 *मिश्रा मार्केट - बिजली बिल*\n\n"
            f"📍 दुकान: *{shop}*\n"
            f"🔢 यूनिट्स: {row.get('Units_Used', 0)}\n"
            f"--------------------------\n"
            f"💵 माह बिल: ₹{curr}\n"
            f"⚠️ बकाया: ₹{pend}\n"
            f"💰 *कुल जमा राशि: ₹{total}*\n"
            f"--------------------------\n"
            f"धन्यवाद। 🙏"
        )
        
        wa_url = f"https://wa.me/91{str(row.get('WhatsApp_No', '')).split('.')[0]}?text={urllib.parse.quote(msg)}"
        st.divider()
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366;color:white;padding:15px;border:none;border-radius:10px;width:100%;font-weight:bold;cursor:pointer;">🟢 व्हाट्सएप पर फाइनल बिल भेजें</button></a>', unsafe_allow_html=True)

else:
    st.error("डेटा लोड करने में समस्या आ रही है।")
    st.info("💡 समाधान: गूगल शीट में 'SHOP_DATA' पन्ने को सबसे पहले (बाएं हाथ पर) रखें।")
