import streamlit as st
import pandas as pd
import urllib.parse
import webbrowser

# आपका सही CSV लिंक (आपके SHEET_ID से)
CSV_URL = "https://docs.google.com/spreadsheets/d/19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo/export?format=csv&gid=0"

# Sheet का Edit लिंक (Entry के लिए)
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo/edit"

@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        return df
    except Exception as e:
        st.error(f"डेटा लोड नहीं हो रहा। CSV लिंक चेक करें या शेयरिंग सही करें।\nएरर: {str(e)}")
        return pd.DataFrame()

df = load_data()

st.set_page_config(page_title="मिश्रा मार्केट मुनीम 👑", layout="wide")
st.title("👑 मिश्रा मार्केट - ब्रिलियंट डिजिटल मुनीम")
st.caption("महीने में 1 बार यूज • डेटा Sheet में हमेशा सुरक्षित")

# सुंदर साइडबार
st.sidebar.title("मेनू")
choice = st.sidebar.radio("", [
    "🏠 डैशबोर्ड",
    "🖋️ रीडिंग + बिल भेजो",
    "💰 पेमेंट + रसीद",
    "📜 रिकॉर्ड भेजो"
])

# डैशबोर्ड को ब्रिलियंट बनाया
if choice == "🏠 डैशबोर्ड":
    st.header("एक नजर में पूरी कहानी")
    
    if df.empty:
        st.warning("डेटा नहीं मिला। CSV लिंक या Sheet शेयरिंग चेक करें।")
    else:
        # कुल अमाउंट
        total_pending = df["Pending_Amount"].astype(float).sum()
        total_payable = df["Total_Payable_Amount"].astype(float).sum()
        
        col1, col2 = st.columns(2)
        col1.metric("कुल पेंडिंग अमाउंट", f"₹{total_pending:,.0f}", delta_color="inverse")
        col2.metric("इस महीने कुल वसूलना", f"₹{total_payable:,.0f}")
        
        # स्टेटस के साथ टेबल (कलरफुल)
        def color_status(val):
            if 'Paid' in str(val):
                return 'background-color: #28a745; color: white'
            elif 'Pending' in str(val):
                return 'background-color: #dc3545; color: white'
            else:
                return 'background-color: #ffc107; color: black'

        styled_df = df.style.format({
            "Total_Payable_Amount": "₹{:,.0f}",
            "Pending_Amount": "₹{:,.0f}",
            "Current_Bill": "₹{:,.0f}"
        }).applymap(color_status, subset=['Status'])

        st.subheader("दुकानों का डिटेल")
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

# रीडिंग + बिल
elif choice == "🖋️ रीडिंग + बिल भेजो":
    st.header("रीडिंग डालो और बिल भेजो")
    shop = st.selectbox("दुकान चुनो", df["Shop_Name"].tolist())
    
    if shop:
        row = df[df["Shop_Name"] == shop].iloc[0]
        prev = float(row.get("Prev_Reading", 0))
        rate = float(row.get("Effective_Unit_Rate", 9.64))
        fixed = float(row.get("Fix_Charge", 222))
        pending = float(row.get("Pending_Amount", 0))
        
        curr = st.number_input("Current Reading डालो", min_value=prev, step=1.0)
        
        if st.button("बिल बनाओ & WhatsApp भेजो"):
            units = curr - prev
            bill = round((units * rate) + fixed)
            total = round(bill + pending)
            
            msg = f"""नमस्ते {shop} जी,
इस महीने का बिल:
Units इस्तेमाल: {units}
Rate: ₹{rate}
Fixed Charge: ₹{fixed}
Current Bill: ₹{bill}
पुराना बकाया: ₹{pending}
कुल जमा करना: ₹{total}

कृपया समय पर जमा करें। धन्यवाद! 🙏"""

            phone = str(row.get("WhatsApp No", "")).replace(" ", "")
            if phone.startswith("91") and len(phone) == 12:
                url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
                webbrowser.open(url)
                st.success("✅ WhatsApp खुल गया! मैसेज भेज दो")
            else:
                st.warning("WhatsApp नंबर चेक करें (91 से शुरू, 12 अंक)")

# पेमेंट + रसीद
elif choice == "💰 पेमेंट + रसीद":
    st.header("पेमेंट रिसीव")
    shop = st.selectbox("दुकान", df["Shop_Name"].tolist())
    amount = st.number_input("मिला अमाउंट (₹)", min_value=0.0, step=10.0)
    mode = st.selectbox("मोड", ["Cash", "UPI", "Bank Transfer"])
    
    if st.button("रसीद भेजो"):
        msg = f"धन्यवाद {shop} जी! ₹{amount} ({mode}) मिल गया। बाकी पेंडिंग चेक कर लें।"
        phone = str(df[df["Shop_Name"] == shop]["WhatsApp No"].values[0]).replace(" ", "")
        url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
        webbrowser.open(url)
        st.success("✅ रसीद WhatsApp पर भेज दी!")

# रिकॉर्ड भेजो
elif choice == "📜 रिकॉर्ड भेजो":
    st.header("पुराना रिकॉर्ड भेजो")
    shop = st.selectbox("दुकान", df["Shop_Name"].tolist())
    if st.button("रिकॉर्ड भेजो"):
        row = df[df["Shop_Name"] == shop].iloc[0]
        msg = f"""{shop} का पूरा रिकॉर्ड:
Prev Reading: {row.get('Prev_Reading', 'N/A')}
Current Reading: {row.get('Curr_Reading', 'N/A')}
Units Used: {row.get('Units_Used', 'N/A')}
Pending Amount: ₹{row.get('Pending_Amount', 0):,.0f}
Total Payable: ₹{row.get('Total_Payable_Amount', 0):,.0f}
Status: {row.get('Status', 'Pending')}"""
        phone = str(row["WhatsApp No"]).replace(" ", "")
        webbrowser.open(f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}")
        st.success("✅ रिकॉर्ड भेज दिया!")

# Sheet Entry बटन
st.sidebar.markdown("---")
st.sidebar.info("रीडिंग/पेमेंट डालने के लिए Sheet खोलो")
if st.sidebar.button("📂 Google Sheet खोलो (Entry करो)"):
    webbrowser.open(SHEET_EDIT_URL)

st.sidebar.info("महीने में 1 बार यूज • सब कुछ Sheet में सुरक्षित 👑")
