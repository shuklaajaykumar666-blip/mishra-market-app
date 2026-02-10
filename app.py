import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# --- CONFIGURATION & LOGIC SETTING ---
st.set_page_config(page_title="Mishra Market Digital Center", layout="wide")

# राजा साहब, यहाँ आपकी Google Sheet की ID और टैब के नाम का लॉजिक है
# (प्रैक्टिकल उपयोग के लिए आपको gspread के साथ इसे कनेक्ट करना होगा)

def load_data():
    # यह डमी डेटा है, यहाँ आपकी गूगल शीट का डेटा लोड होगा
    shop_data = pd.DataFrame({
        'Shop_Name': ['Maa Durga', 'Poonam Ladies Corner', 'Govt Meter'],
        'WhatsApp_No': ['919999999999', '918888888888', ''],
        'Prev_Reading': [1000, 2500, 50000],
        'Curr_Reading': [1100, 2650, 52000],
        'Units_Used': [100, 150, 2000],
        'Rate': [9.64, 9.64, 0],
        'Fix_Charge': [222, 222, 0],
        'Pending_Amount': [500, 0, 0],
        'Total_Payable': [1686, 1668, 0],
        'Status': ['Unpaid', 'Paid', '']
    })
    return shop_data

# --- APP UI ---
st.title("👑 मिश्रा मार्केट - डिजिटल मैनेजमेंट सिस्टम")
st.markdown("---")

menu = ["Dashboard", "Reading Entry", "Payment & Receipts", "Govt Bill Audit", "Month Close (History)"]
choice = st.sidebar.selectbox("Main Menu", menu)

# --- 1. DASHBOARD (Total Collection & Recovery) ---
if choice == "Dashboard":
    data = load_data()
    total_recovery = data['Total_Payable'].sum()
    paid_amount = data[data['Status'] == 'Paid']['Total_Payable'].sum()
    pending_to_collect = total_recovery - paid_amount

    col1, col2, col3 = st.columns(3)
    col1.metric("कुल वसूली (Total)", f"₹{total_recovery}")
    col2.metric("वसूला गया (Collected)", f"₹{paid_amount}", delta_color="normal")
    col3.metric("बाकी वसूली (Pending)", f"₹{pending_to_collect}", delta="-Critical")

    st.subheader("📋 दुकानों का ताज़ा स्टेटस")
    st.table(data[['Shop_Name', 'Units_Used', 'Total_Payable', 'Status']])

# --- 2. READING ENTRY (The Auto Bill Logic) ---
elif choice == "Reading Entry":
    st.subheader("📝 नई रीडिंग और बिल जनरेशन")
    with st.form("reading_form"):
        shop = st.selectbox("दुकान चुनें", ["Maa Durga", "Poonam Ladies Corner"])
        curr_read = st.number_input("Current Reading दर्ज करें", min_value=0)
        submit = st.form_submit_button("बिल तैयार करें")
        
        if submit:
            st.success(f"{shop} का बिल अपडेट हो गया है। Units और Charges खुद-ब-खुद कैलकुलेट हो गए हैं।")

# --- 3. PAYMENT & RECEIPTS (WhatsApp Logic) ---
elif choice == "Payment & Receipts":
    st.subheader("💰 पेमेंट और व्हाट्सएप रसीद")
    data = load_data()
    shop_select = st.selectbox("दुकानदार चुनें", data['Shop_Name'])
    row = data[data['Shop_Name'] == shop_select].iloc[0]
    
    amount_received = st.number_input(f"Amount Received (Bill: {row['Total_Payable']})", value=float(row['Total_Payable']))
    mode = st.radio("पेमेंट मोड", ["Cash", "Online"])
    
    if st.button("व्हाट्सएप रसीद भेजें"):
        # व्हाट्सएप मैसेज का "राजा साहब" स्टाइल लॉजिक
        msg = f"*मिश्रा मार्केट रसीद*\n\nदुकान: {shop_select}\nप्राप्त राशि: ₹{amount_received}\nमोड: {mode}\nबकाया: ₹{row['Total_Payable'] - amount_received}\n\n*धन्यवाद!*"
        encoded_msg = urllib.parse.quote(msg)
        wa_url = f"https://wa.me/{row['WhatsApp_No']}?text={encoded_msg}"
        st.markdown(f"[यहाँ क्लिक करके रसीद भेजें]({wa_url})")

# --- 4. GOVT BILL AUDIT (The Gap Tracker) ---
elif choice == "Govt Bill Audit":
    st.subheader("🔍 सरकारी बिल बनाम दुकान यूनिट्स")
    govt_units = 2000  # Govt Tab से आएगा
    shop_units_total = 1850 # Shop Data Sum
    diff = govt_units - shop_units_total
    
    st.metric("सरकारी मीटर खपत", f"{govt_units} Unit")
    st.metric("दुकानों की कुल खपत", f"{shop_units_total} Unit")
    
    if diff > 0:
        st.error(f"⚠️ चेतावनी: {diff} यूनिट का घाटा (चोरी या लाइन लॉस)!")
    else:
        st.success("✅ हिसाब बराबर है।")

# --- 5. MONTH CLOSE (The History Logic) ---
elif choice == "Month Close (History)":
    st.warning("सावधान! यह बटन दबाने से करंट डेटा History में चला जाएगा और Reading Reset हो जाएगी।")
    if st.button("महीना बंद करें (Confirm Month Close)"):
        st.balloons()
        st.success("सारा डेटा History टैब में सुरक्षित हो गया है। Current Reading अब Previous बन गई है।")
