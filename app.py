import streamlit as st
import pandas as pd
import urllib.parse
import webbrowser

# --- Google Sheet PUBLIC CSV Export (Read Only, 100% फ्री) ---
# अपना Sheet का PUBLIC CSV लिंक डालो (File → Share → Publish to web → CSV)
# या export लिंक: https://docs.google.com/spreadsheets/d/SHEET_ID/export?format=csv&gid=0
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=0"  # <-- अपना SHEET_ID डालो

@st.cache_data(ttl=300)  # हर 5 मिनट रिफ्रेश
def load_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        return df
    except:
        st.error("Sheet लोड नहीं हो रहा। PUBLIC CSV लिंक चेक करें।")
        return pd.DataFrame()

df = load_data()

# --- ऐप सेटिंग ---
st.set_page_config(page_title="मिश्रा मार्केट मुनीम 👑", layout="wide")
st.title("मिश्रा मार्केट - WhatsApp बिलिंग सिस्टम (PDF फ्री)")

# साइडबार मेनू
choice = st.sidebar.radio("मेनू", [
    "डैशबोर्ड",
    "रीडिंग एंट्री & WhatsApp बिल",
    "पेमेंट एंट्री",
    "सरकारी गैप चेक"
])

if choice == "डैशबोर्ड":
    st.header("एक नजर में")
    if not df.empty:
        total_pending = df.get('Pending_Amount', pd.Series(0)).astype(float).sum()
        st.metric("कुल पेंडिंग", f"₹{total_pending:,.0f}")
        st.dataframe(df.style.format({"Total_Payable_Amount": "₹{:,.0f}"}), use_container_width=True)

elif choice == "रीडिंग एंट्री & WhatsApp बिल":
    st.header("Current Reading डालें → WhatsApp बिल")
    shop = st.selectbox("दुकान", df['Shop_Name'].tolist() if 'Shop_Name' in df else [])
    
    if shop:
        row = df[df['Shop_Name'] == shop].iloc[0]
        prev = float(row.get('Prev_Reading', 0))
        rate = float(row.get('Effective_Unit_Rate', 9.64))
        fixed = float(row.get('Fixed_Charge', 222))
        pending = float(row.get('Pending_Amount', 0))
        
        curr = st.number_input("Current Reading", min_value=prev)
        
        if st.button("बिल कैलकुलेट & WhatsApp भेजें"):
            units = curr - prev
            bill = (units * rate) + fixed
            total = round(bill + pending)
            
            msg = f"""नमस्ते {shop} जी,
इस महीने:
Units: {units}
Rate: ₹{rate}
Fixed: ₹{fixed}
Current Bill: ₹{bill:,.0f}
पुराना बकाया: ₹{pending:,.0f}
कुल जमा: ₹{total}

समय पर जमा करें। धन्यवाद! 🙏"""
            
            phone = str(row.get('WhatsApp No', ''))
            if phone.startswith('91') and len(phone) == 12:
                url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
                webbrowser.open(url)
                st.success("WhatsApp खुल गया! मैसेज भेजें।")
            else:
                st.warning("WhatsApp नंबर चेक करें (91 से शुरू, 12 अंक)")

elif choice == "पेमेंट एंट्री":
    st.header("पेमेंट रिसीव्ड")
    shop = st.selectbox("दुकान", df['Shop_Name'].tolist())
    amount = st.number_input("मिला अमाउंट", min_value=0.0)
    mode = st.selectbox("मोड", ["Cash", "UPI"])
    
    if st.button("Save & रसीद भेजें"):
        st.success(f"₹{amount} सेव! {shop} को रसीद भेजी जा सकती है।")
        # यहां असली में Sheet अपडेट लॉजिक ऐड करो (write के लिए service account जरूरी)
        phone = "91xxxxxxxxxx"  # डायनामिक करो
        msg = f"धन्यवाद! ₹{amount} ({mode}) मिला। बाकी चेक करें।"
        url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
        webbrowser.open(url)

elif choice == "सरकारी गैप चेक":
    st.header("सरकारी vs दुकानें गैप")
    govt_units = df[df['Shop_Name'] == "सरकारी मीटर"]['Units_Used'].values[0] if 'सरकारी मीटर' in df['Shop_Name'].values else 0
    shop_units = df[df['Shop_Name'] != "सरकारी मीटर"]['Units_Used'].astype(float).sum()
    gap = govt_units - shop_units
    st.metric("गैप (लॉस/चोरी?)", gap, delta_color="inverse" if gap > 0 else "normal")

st.sidebar.info("PDF फ्री वर्जन | सिर्फ WhatsApp से काम | हमेशा फ्री 👑")
