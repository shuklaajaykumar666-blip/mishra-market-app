import streamlit as st
import pandas as pd
from gspread_streamlit import gspread_client
from datetime import datetime

# गूगल शीट का लिंक (राजा साहब इसे बदल सकते हैं)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1kUci8cSZ2UQz7uUL7BLFbcxcLspgtyO-zmBjyukPPno/edit"

st.set_page_config(page_title="Mishra Market App", layout="wide")
st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग सिस्टम")

# गूगल शीट से जुड़ने का लॉजिक
try:
    gc = gspread_client.get_client()
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.get_worksheet(0)
    gov_worksheet = sh.worksheet("GOV_BILL")
except:
    st.error("कृपया गूगल शीट को Editor एक्सेस दें और GOV_BILL टैब चेक करें।")
    st.stop()

# डेटा लोड करना
data = pd.DataFrame(worksheet.get_all_records())

tab1, tab2, tab3, tab4 = st.tabs(["📊 बिलिंग", "💰 पेमेंट", "🔌 सरकारी डेटा", "⚙️ मैनेजमेंट"])

with tab1:
    st.subheader("दुकान की रीडिंग भरें")
    if not data.empty:
        selected_shop = st.selectbox("दुकान चुनें", data['Shop_Name'])
        idx = data[data['Shop_Name'] == selected_shop].index[0]
        
        col1, col2 = st.columns(2)
        with col1:
            prev = st.number_input("पुरानी रीडिंग", value=float(data.at[idx, 'Prev_Reading']), disabled=True)
            curr = st.number_input("नई रीडिंग डालें", value=float(data.at[idx, 'Curr_Reading']))
        
        with col2:
            units = curr - prev
            bill = (units * 9.64) + 222 if units > 0 else 0
            st.metric("इस महीने का बिल", f"₹{bill:.2f}")

        if st.button("बिल अपडेट करें और WhatsApp भेजें"):
            worksheet.update_cell(idx + 2, 4, curr) # Curr_Reading column
            msg = f"नमस्ते {selected_shop}, आपका बिजली बिल: यूनिट {units}, कुल बकाया राशि ₹{data.at[idx, 'Total_Amount']}।"
            wa_link = f"https://wa.me/{data.at[idx, 'WhatsApp_No']}?text={msg}"
            st.success("डेटा सेव हो गया!")
            st.markdown(f"[📲 यहाँ क्लिक करके WhatsApp भेजें]({wa_link})")

with tab3:
    st.subheader("सरकारी मीटर रिकॉर्ड")
    # यहाँ सरकारी डेटा का लॉजिक रहेगा

# फाइल के अंत में Commit बटन दबाना न भूलें!
