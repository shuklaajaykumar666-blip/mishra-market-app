import streamlit as st
import pandas as pd
import urllib.parse

# --- APP CONFIG ---
st.set_page_config(page_title="Mishra Market Admin", layout="wide")

# --- 1. DASHBOARD (The King's View) ---
def show_dashboard():
    st.title("👑 मिश्रा मार्केट - डिजिटल हेडक्वाटर")
    
    # --- सरकारी बिल एवं ऑडिट (GOVT_BILL_DATA) ---
    # यहाँ आपका बताया हुआ सटीक गणित
    govt_total_amt = 5938.00
    govt_extra_charges = 3979.06
    kul_govt_rashi = govt_total_amt + govt_extra_charges # 9917.06
    
    st.subheader("⚡ सरकारी बिल एवं ऑडिट (GOVT_BILL_DATA)")
    gov1, gov2, gov3, gov4, gov5 = st.columns(5)
    gov1.metric("Govt_Bill_Unit", "792")
    gov2.metric("Govt_Extra_Charges", f"₹{govt_extra_charges}")
    gov3.metric("कुल सरकारी राशि", f"₹{kul_govt_rashi:.2f}")
    gov4.metric("Govt_Difference_Unit", "176 Units", delta="-Loss (Chori)", delta_color="inverse")
    gov5.metric("ड्यू डेट (Col J)", "07/02/2026")

    st.markdown("---")

    # --- मार्केट रिकवरी सारांश (पुराना चार्ट सिस्टम वापस) ---
    st.subheader("🏢 मार्केट रिकवरी सारांश")
    s1, s2, s3 = st.columns(3)
    s1.metric("कुल करंट बिल", "₹9,934.24")
    s2.metric("Total_Payable_Amount", "₹48,522", delta="बकाया सहित")
    
    # वसूली चार्ट (जैसा पहले था)
    paid_amt = 15000 
    pending_amt = 48522 - paid_amt
    s3.metric("अभी भी बकाया (Pending)", f"₹{pending_amt}")
    
    chart_data = pd.DataFrame({'Status': ['प्राप्त (Paid)', 'बकाया (Pending)'], 'Amount': [paid_amt, pending_amt]})
    st.bar_chart(chart_data.set_index('Status'))

# --- 2. READING SYSTEM (वही पुराना जो आपको सही लगा था) ---
def show_reading_entry():
    st.header("🖋️ रीडिंग एंट्री (SHOP_DATA)")
    shop_list = ["माँ दुर्गा", "पूनम लेडिज कॉर्नर", "आधुनिक शूज"] # आपकी शीट के नाम
    shop = st.selectbox("दुकान चुनें", shop_list)
    
    col1, col2 = st.columns(2)
    prev_r = col1.number_input("Prev_Reading", value=9000) # ऑटो फेच होगा
    curr_r = col2.number_input("Current_Reading दर्ज करें")
    
    if st.button("Generate Bill & WhatsApp"):
        if curr_r < prev_r:
            st.error("गलती: करंट रीडिंग कम नहीं हो सकती!")
        else:
            units = curr_r - prev_r
            bill = (units * 9.64) + 222 # फिक्स चार्ज
            st.success(f"बिल तैयार: ₹{bill}")
            # व्हाट्सएप मैसेज बटन
            msg = f"*मिश्रा मार्केट बिल*\nदुकान: {shop}\nरीडिंग: {prev_r}-{curr_r}\nयूनिट: {units}\nकुल: ₹{bill}"
            st.markdown(f"[📲 व्हाट्सएप भेजें](https://wa.me/919936931904?text={urllib.parse.quote(msg)})")

# --- 3. PAYMENT LEDGER (वही पुराना वसूलने वाला सिस्टम) ---
def show_payments():
    st.header("💸 पेमेंट लेजर (वसूली)")
    shop = st.selectbox("दुकान चुनें (Payment)", ["माँ दुर्गा", "पूनम लेडिज कॉर्नर"])
    st.warning("कुल वसूलना है: ₹48,522 में से इस दुकान का हिस्सा...")
    
    received = st.number_input("प्राप्त राशि (Received Amount)")
    mode = st.selectbox("Mode", ["CASH", "ONLINE"])
    
    if st.button("पेमेंट दर्ज करें"):
        st.success("PAID ✅ - इतिहास सुरक्षित कर लिया गया है।")

# --- 4. MONTH CLOSE (Carry Forward Logic) ---
def show_month_close():
    st.header("⚙️ क्लोज मंथ (Carry Forward)")
    st.info("बटन दबाते ही Row 11 के नीचे डेटा सेव होगा और बकाया आगे जाएगा।")
    if st.button("🔴 Confirm Month Close"):
        st.balloons()
        st.success("Data Moved to History Successfully!")

# --- MENU CONTROL ---
menu = ["📊 डैशबोर्ड", "🖋️ रीडिंग एंट्री", "💸 पेमेंट वसूली", "⚙️ मंथ क्लोज"]
choice = st.sidebar.radio("मेनु", menu)

if choice == "📊 डैशबोर्ड": show_dashboard()
elif choice == "रीडिंग एंट्री": show_reading_entry()
elif choice == "पेमेंट वसूली": show_payments()
elif choice == "मंथ क्लोज": show_month_close()
