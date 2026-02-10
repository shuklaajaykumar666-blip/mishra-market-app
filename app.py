import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="मिश्रा मार्केट", layout="wide")

# डेटा लिंक
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        # कॉलम के नामों में से फालतू स्पेस हटाना ताकि एरर न आए
        df.columns = [str(c).strip() for c in df.columns]
        return df.dropna(subset=[df.columns[0]]) # पहले कॉलम (Shop Name) के आधार पर खाली लाइनें हटाना
    except Exception as e:
        st.error(f"Sheet Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("👑 मिश्रा मार्केट बिलिंग")
    
    # --- टैब ---
    tab1, tab2 = st.tabs(["📋 पूरी लिस्ट", "🧾 व्हाट्सएप बिल भेजें"])

    with tab1:
        st.subheader("पूरी दुकान लिस्ट (जैसा शीट में है)")
        # सीधे आपकी शीट का डेटा दिखा रहा है
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.subheader("दुकान चुनें")
        # आपकी शीट का पहला कॉलम (दुकान का नाम) उठाएगा
        shop_col = df.columns[0] 
        shop_list = df[shop_col].unique()
        selected_shop = st.selectbox("दुकानदार का नाम:", shop_list)
        
        row = df[df[shop_col] == selected_shop].iloc[0]

        # शीट से सीधा डेटा दिखाना (जो कॉलम उपलब्ध हैं वही दिखाएगा)
        st.write("---")
        cols = st.columns(len(df.columns[:6])) # पहले 6 कॉलम दिखाने के लिए
        for i, col_name in enumerate(df.columns[:6]):
            cols[i % len(cols)].metric(col_name, row[col_name])

        st.write("---")
        
        # व्हाट्सएप मैसेज (हम मान रहे हैं कि आपकी शीट में ये कॉलम नाम हैं)
        # अगर नाम थोड़े अलग भी हुए तो यह एरर नहीं देगा, खाली छोड़ देगा
        try:
            wa_no = str(row.get('WhatsApp No', row.get('WhatsApp_No', ''))).split('.')[0]
            curr_bill = row.get('Current_Bill', row.get('Current Bill', '0'))
            pend_bill = row.get('Pending Balance', row.get('Pending_Balance', '0'))
            total_bill = row.get('Total Amount', row.get('Total_Amount', row.get('Total Amount', '0')))
            units = row.get('Units Used', row.get('Units_Used', '0'))

            message = (
                f"👑 *मिश्रा मार्केट - बिजली बिल*\n\n"
                f"📍 दुकान: *{selected_shop}*\n"
                f"🔢 यूनिट्स: {units}\n"
                f"--------------------------\n"
                f"💵 माह बिल: ₹{curr_bill}\n"
                f"⚠️ बकाया: ₹{pend_bill}\n"
                f"💰 *कुल देय राशि: ₹{total_bill}*\n"
                f"--------------------------\n"
                f"धन्यवाद। 🙏"
            )
            
            if wa_no:
                encoded_msg = urllib.parse.quote(message)
                wa_url = f"https://wa.me/91{wa_no}?text={encoded_msg}"
                st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366;color:white;padding:15px;border:none;border-radius:10px;width:100%;font-weight:bold;cursor:pointer;">🟢 व्हाट्सएप पर बिल भेजें</button></a>', unsafe_allow_html=True)
            else:
                st.warning("व्हाट्सएप नंबर नहीं मिला।")
        except Exception as e:
            st.error("व्हाट्सएप मैसेज तैयार करने में दिक्कत आ रही है।")

else:
    st.warning("डेटा लोड नहीं हो पाया। अपनी शीट चेक करें।")
