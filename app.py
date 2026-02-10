import streamlit as st
import pandas as pd
import urllib.parse
import webbrowser

# ==================== अपना CSV लिंक यहाँ डालो ====================
CSV_URL = "https://docs.google.com/spreadsheets/d/19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo/edit?gid=731375192#gid=731375192/export?format=csv"
# =================================================================

@st.cache_data(ttl=300)
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()

st.set_page_config(page_title="मिश्रा मार्केट मुनीम", layout="wide")
st.title("👑 मिश्रा मार्केट - Digital Munim")
st.caption("महीने में 1 बार यूज • सब कुछ Sheet में सुरक्षित")

# Sidebar
choice = st.sidebar.radio("मेनू चुनो", [
    "📋 डैशबोर्ड",
    "🖋️ रीडिंग डालो + बिल भेजो",
    "💰 पेमेंट + रसीद भेजो",
    "📜 पुराना रिकॉर्ड भेजो"
])

if choice == "📋 डैशबोर्ड":
    st.header("आज का पूरा हिसाब")
    st.dataframe(df.style.format({"Total_Payable_Amount": "₹{:,.0f}"}), use_container_width=True)

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
Units: {units}
Rate: ₹{rate}
Fixed Charge: ₹{fixed}
Current Bill: ₹{bill}
पुराना बकाया: ₹{pending}
कुल जमा करना: ₹{total}

कृपया समय पर जमा करें। 🙏"""

            phone = str(row["WhatsApp No"]).replace(" ", "")
            if phone.startswith("91"):
                url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
                webbrowser.open(url)
                st.success("✅ WhatsApp खुल गया! मैसेज भेज दो")
            else:
                st.warning("WhatsApp नंबर गलत है")

elif choice == "💰 पेमेंट + रसीद भेजो":
    st.header("पेमेंट रिसीव")
    shop = st.selectbox("दुकान", df["Shop_Name"].tolist())
    amount = st.number_input("मिला अमाउंट (₹)", min_value=0.0)
    mode = st.selectbox("मोड", ["Cash", "UPI", "Bank"])
    
    if st.button("रसीद भेजो"):
        msg = f"धन्यवाद {shop} जी! ₹{amount} ({mode}) मिल गया। बाकी पेंडिंग चेक कर लें।"
        phone = str(df[df["Shop_Name"] == shop]["WhatsApp No"].values[0]).replace(" ", "")
        url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
        webbrowser.open(url)
        st.success("✅ रसीद WhatsApp पर भेज दी!")

elif choice == "📜 पुराना रिकॉर्ड भेजो":
    st.header("रिकॉर्ड भेजो")
    shop = st.selectbox("दुकान", df["Shop_Name"].tolist())
    if st.button("रिकॉर्ड WhatsApp पर भेजो"):
        row = df[df["Shop_Name"] == shop].iloc[0]
        msg = f"""{shop} का पूरा रिकॉर्ड:
Prev Reading : {row['Prev_Reading']}
Current Reading : {row['Curr_Reading']}
Units : {row['Units_Used']}
Pending : ₹{row['Pending_Amount']}
Total Payable : ₹{row['Total_Payable_Amount']}
Status : {row.get('Status', 'Pending')}"""
        phone = str(row["WhatsApp No"]).replace(" ", "")
        webbrowser.open(f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}")
        st.success("✅ रिकॉर्ड भेज दिया!")

st.sidebar.info("Entry के लिए नीचे बटन दबाओ")
if st.sidebar.button("📂 Google Sheet खोलो (Entry के लिए)"):
    sheet_edit_url = "https://docs.google.com/spreadsheets/d/19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo/edit?gid=731375192#gid=731375192/edit"
    webbrowser.open(sheet_edit_url)
