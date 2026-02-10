import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mishra Market", layout="wide")

# सबसे सरल और पक्का लिंक (बिना GID के, यह पहले पन्ने को उठाएगा)
# पक्का करें कि SHOP_DATA आपकी शीट का पहला टैब (पन्ना) है
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=10) # यहाँ समय कम कर दिया ताकि तुरंत अपडेट दिखे
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip()
        # अगर Shop_Name कॉलम है तभी आगे बढ़ें
        if 'Shop_Name' in df.columns:
            return df.dropna(subset=['Shop_Name'])
        return df
    except Exception as e:
        return str(e)

st.title("👑 मिश्रा मार्केट बिलिंग")

data = load_data()

# अगर डेटा लोड हो गया
if isinstance(data, pd.DataFrame):
    if not data.empty:
        st.success("✅ डेटा सफलतापूर्वक जुड़ गया है!")
        
        # बिल कार्ड्स
        c1, c2 = st.columns(2)
        bill_sum = pd.to_numeric(data.get('Current_Bill', 0), errors='coerce').sum()
        c1.metric("कुल बिल", f"₹{bill_sum:,.2f}")
        c2.metric("कुल दुकानें", len(data))

        st.divider()
        
        # चार्ट
        if 'Current_Bill' in data.columns:
            fig = px.bar(data, x='Shop_Name', y='Current_Bill', title="मार्केट बिल ग्राफ")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 पूरी लिस्ट")
        st.dataframe(data)
    else:
        st.warning("शीट तो खुल गई, पर शायद पहला पन्ना खाली है।")
else:
    # अगर एरर आए तो यहाँ दिखेगा
    st.error(f"कनेक्शन में अभी भी दिक्कत है: {data}")
    st.info("सुझाव: अपनी गूगल शीट में 'SHOP_DATA' वाले टैब को पकड़ कर सबसे आगे (बाएं तरफ) कर दें।")
