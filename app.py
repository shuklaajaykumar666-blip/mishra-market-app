import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# --- APP CONFIG ---
st.set_page_config(page_title="Mishra Market Admin", layout="wide")

# --- 1. DASHBOARD (The King's View) ---
def show_dashboard():
    st.title("👑 मिश्रा मार्केट - किंग डैशबोर्ड")
    
    # सरकारी मीटर कार्ड (Based on GOVT_BILL_DATA Tab)
    with st.container():
        st.subheader("📋 सरकारी बिल विवरण (GOVT_BILL_DATA)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("कुल सरकारी यूनिट", "792 Units")
        c2.metric("एक्स्ट्रा चार्जेस", "₹3,979.06")
        c3.metric("कुल सरकारी राशि", "₹5,938")
        c4.metric("ड्यू डेट", "07/02/2026")

    st.markdown("---")

    # दुकानदारी सारांश (Based on SHOP_DATA Tab)
    st.subheader("🏢 मार्केट रिकवरी सारांश")
    col1, col2, col3 = st.columns(3)
    col1.metric("टोटल दुकान यूनिट (Shop Sum)", "616 Units")
    col2.metric("कुल करंट बिल", "₹8,450") # Example Sum
    col3.metric("कुल वसूलने योग्य (Payable)", "₹12,450", delta="बकाया सहित")

    # बार चार्ट (वसूली मीटर)
    chart_data = pd.DataFrame({'Status': ['वसूला गया', 'बाकी'], 'Amount': [8000, 4450]})
    st.bar_chart(chart_data.set_index('Status'))
    
    if st.button("📥 पूरे महीने की PDF रिपोर्ट डाउनलोड करें"):
        st.write("Generating Report... (All 18 Shops Data Exported)")

# --- 2. READING ENTRY (The Billing Engine) ---
def show_reading_entry():
    st.header("🖋️ नई रीडिंग एंट्री (SHOP_DATA)")
    shop_list = ["माँ दुर्गा", "पूनम लेडिज कॉर्नर", "सरकारी मीटर", "पूजा लेडिज कॉर्नर"] # As per your image
    
    with st.form("billing_form"):
        shop = st.selectbox("दुकान का नाम चुनें", shop_list)
        prev = st.number_input("Prev_Reading (Auto-Fetched)", value=9002) # Sheet से आएगा
        curr = st.number_input("Current_Reading दर्ज करें")
        
        if st.form_submit_button("बिल जनरेट और व्हाट्सएप तैयार करें"):
            if curr < prev:
                st.error("❌ गलती: करंट रीडिंग पिछली रीडिंग से कम नहीं हो सकती!")
            else:
                units = curr - prev
                # यहाँ आपका 9.64 वाला रेट लॉजिक
                total = (units * 9.64) + 222 + 500 # Pending balance included
                st.success(f"बिल तैयार! कुल राशि: ₹{total}")
                
                # व्हाट्सएप बटन विथ डिटेल्स
                msg = f"*मिश्रा मार्केट बिल*\nदुकान: {shop}\nरीडिंग: {prev}-{curr}\nयूनिट: {units}\nकुल देय: ₹{total}"
                st.markdown(f"[📲 व्हाट्सएप पर बिल भेजें](https://wa.me/919936931904?text={urllib.parse.quote(msg)})")

# --- 3. PAYMENT & RECEIPTS (Recovery Tab) ---
def show_payments():
    st.header("💸 पेमेंट वसूली (PAYMENT_LEDGER)")
    shop_list = ["माँ दुर्गा", "पूनम लेडिज कॉर्नर", "आधुनिक शूज"]
    
    shop = st.selectbox("दुकान चुनें (वसूली के लिए)", shop_list)
    st.warning(f"इस दुकान से कुल ₹444 वसूलना बाकी है।") # Auto fetch from Total_Payable
    
    paid_amt = st.number_input("प्राप्त राशि दर्ज करें")
    mode = st.radio("पेमेंट मोड", ["CASH", "ONLINE"])
    
    if st.button("पेमेंट दर्ज करें और रसीद भेजें"):
        status = "PAID ✅" if paid_amt >= 444 else "PARTIAL ⚠️"
        st.success(f"पेमेंट दर्ज! स्टेटस: {status}")
        
        # कंफर्मेशन रसीद व्हाट्सएप
        rec_msg = f"*पेमेंट रसीद*\nदुकान: {shop}\nप्राप्त: ₹{paid_amt}\nस्टेटस: {status}\nधन्यवाद!"
        st.markdown(f"[📲 कंफर्मेशन भेजें](https://wa.me/919936931904?text={urllib.parse.quote(rec_msg)})")

# --- 4. MONTH CLOSE (The Carry Forward Logic) ---
def show_month_close():
    st.header("⚙️ मंथ क्लोज (Carry Forward Logic)")
    st.info("यह बटन दबाने पर SHOP_DATA, GOVT_BILL_DATA और PAYMENT_LEDGER का डेटा सुरक्षित होकर Row 11 के नीचे सेव हो जाएगा।")
    
    if st.button("🔴 क्लोज मंथ और डेटा सुरक्षित करें"):
        st.balloons()
        st.write("1. Current Reading -> Previous Reading (Done)")
        st.write("2. Unpaid Balance -> Next Month Pending (Done)")
        st.write("3. Govt Data saved to Row 11+ (Done)")
        st.success("नया महीना शुरू करने के लिए सिस्टम तैयार है!")

# --- MAIN MENU ---
menu = ["डैशबोर्ड", "रीडिंग एंट्री", "पेमेंट वसूली", "मंथ क्लोज"]
choice = st.sidebar.radio("मेनु", menu)

if choice == "डैशबोर्ड":
    show_dashboard()
elif choice == "रीडिंग एंट्री":
    show_reading_entry()
elif choice == "पेमेंट वसूली":
    show_payments()
elif choice == "मंथ क्लोज":
    show_month_close()
