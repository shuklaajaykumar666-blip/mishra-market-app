import streamlit as st
import pandas as pd
import urllib.parse
import webbrowser

# आपका सही CSV लिंक (आपके SHEET_ID से बना)
CSV_URL = "https://docs.google.com/spreadsheets/d/19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo/export?format=csv&gid=0"

# Sheet का Edit लिंक (Entry के लिए)
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo/edit"

@st.cache_data(ttl=300)
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()

st.set_page_config(page_title="मिश्रा मार्केट मुनीम 👑", layout="wide")
st.title("मिश्रा मार्केट - Digital Munim")
st.caption("महीने में 1 बार यूज • सब कुछ Sheet में सुरक्षित")

choice = st.sidebar.radio("मेनू चुनो", [
    "📋 डैशबोर्ड",
    "🖋️ रीडिंग डालो + बिल भेजो",
    "💰 पेमेंट + रसीद भेजो",
    "📜 पुराना रिकॉर्ड भेजो"
])

if choice == "📋 डैशबोर्ड":
    st.header("आज का पूरा हिसाब")
    st.dataframe(
        df.style.format({"Total_Payable_Amount": "₹{:,.0f}", "Pending_Amount": "₹{:,.0f}"}),
        use_container_width=True
    )

elif choice == "🖋️ रीडिंग डालो + बिल भेजो":
    st.header("रीडिंग एंट्री")
    shop = st.selectbox("दुकान चुनो", df["Shop_Name"].tolist())
    
    if shop:
        row = df[df["Shop_Name"] == shop].iloc[0]
        prev = float(row["Prev_Reading"])
        rate = float(row.get("Effective_Unit_Rate", 9.64))
        fixed = float(row.get("Fix_Charge", 222))
        pending = float(row.get("Pending_Amount", 0))
        
        curr = st.number_input("Current Reading डालो", min_value=prev)
        
        if st.button("बिल तैयार करो & WhatsApp भेजो"):
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

कृपया जल्दी जमा करें। धन्यवाद! 🙏"""

            phone = str(row["WhatsApp No"]).replace(" ", "")
            if phone.startswith("91") and len(phone) == 12:
                url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
                webbrowser.open(url)
                st.success("✅ WhatsApp खुल गया! मैसेज भेज दो")
            else:
                st.warning("WhatsApp नंबर चेक करें (91 से शुरू, 12 अंक)")

elif choice == "💰 पेमेंट + रसीद भेजो":
    st.header("पेमेंट रिसीव")
    shop = st.selectbox("दुकान", df["Shop_Name"].tolist())
    amount = st.number_input("मिला अमाउंट (₹)", min_value=0.0)
    mode = st.selectbox("मोड", ["Cash", "UPI", "Bank Transfer"])
    
    if st.button("रसीद भेजो"):
        msg = f"धन्यवाद {shop} जी! ₹{amount} ({mode}) मिल गया। बाकी पेंडिंग चेक कर लें।"
        phone = str(df[df["Shop_Name"] == shop]["WhatsApp No"].values[0]).replace(" ", "")
        if phone.startswith("91"):
            webbrowser.open(f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}")
            st.success("✅ रसीद WhatsApp पर भेज दी!")
        else:
            st.warning("नंबर चेक करें")

elif choice == "📜 पुराना रिकॉर्ड भेजो":
    st.header("रिकॉर्ड भेजो")
    shop = st.selectbox("दुकान", df["Shop_Name"].tolist())
    if st.button("रिकॉर्ड WhatsApp पर भेजो"):
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

# Sheet खोलने का बटन (Entry के लिए)
st.sidebar.markdown("---")
st.sidebar.info("रीडिंग/पेमेंट डालने के लिए Sheet खोलो")
if st.sidebar.button("📂 Google Sheet खोलो (Entry करो)"):
    webbrowser.open("https://docs.google.com/spreadsheets/d/19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo/edit")

st.sidebar.info("महीने में 1 बार यूज • सब कुछ Sheet में सुरक्षित 👑")
