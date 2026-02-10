import streamlit as st
import pandas as pd
import urllib.parse

# --- Google Sheet कनेक्ट करने के लिए (अभी कमेंटेड - बाद में अनकमेंट करो) ---
# import gspread
# from google.oauth2.service_account import Credentials
# creds = Credentials.from_service_account_file("credentials.json", scopes=...)
# client = gspread.authorize(creds)
# sheet = client.open_by_key("YOUR_SHEET_ID").worksheet("SHOP_DATA")
# data = sheet.get_all_records()
# df = pd.DataFrame(data)

# अभी के लिए हार्डकोडेड डेटा (आपकी असली शीट का सैंपल)
def get_market_data():
    columns = ["Shop_Name", "WhatsApp No", "Prev_Reading", "Curr_Reading", "Units_Used", 
               "Effective_Unit_Rate", "Fix_Charge", "Current_Bill", "Pending Balance", 
               "Total_Amount", "Status"]
    data = [
        ["माँ दुर्गा", "919936xxxxxx", 9002, 9050, 48, 9.64, 222, 684.72, 0, 684.72, "Paid ✅"],
        ["पूनम लेडिज", "919936xxxxxx", 791, 850, 59, 9.64, 222, 790.76, 500, 1290.76, "Pending ❌"],
        ["सरकारी मीटर", "N/A", 594, 770, 176, 0, 0, 0, 5228, 5228, "Loss Area"],
        ["पूजा लेडिज", "919936xxxxxx", 653, 710, 57, 9.64, 222, 771.48, 1088, 1859.48, "Pending ❌"],
        # नई दुकानें यहाँ ऐड कर सकते हो
    ]
    df = pd.DataFrame(data, columns=columns)
    # ऑटो कैलकुलेशन अगर Curr_Reading अपडेट हो
    df['Units_Used'] = df['Curr_Reading'] - df['Prev_Reading']
    df['Current_Bill'] = (df['Units_Used'] * df['Effective_Unit_Rate']) + df['Fix_Charge']
    df['Total_Amount'] = df['Current_Bill'] + df['Pending Balance']
    df['Total_Amount'] = df['Total_Amount'].round(0).astype(int)  # राउंडिंग जैसा आप करते हो
    return df

# --- ऐप सेटिंग ---
st.set_page_config(page_title="Mishra Market Admin 👑", layout="wide")

# --- साइडबार मेनू ---
st.sidebar.title("👑 मिश्रा मार्केट एडमिन")
choice = st.sidebar.radio("मेनू चुनें", [
    "📋 पूरी शॉप लिस्ट (Live View)",
    "🖋️ नई रीडिंग + बिल जनरेट",
    "💰 पेमेंट एंट्री",
    "📊 सरकारी ऑडिट & गैप चेक"
])

df = get_market_data()

# --- 1. पूरी लिस्ट ---
if choice == "📋 पूरी शॉप लिस्ट (Live View)":
    st.title("📋 मिश्रा मार्केट - लाइव रजिस्टर")
    
    search = st.text_input("🔍 दुकान नाम सर्च करें...")
    filtered = df if not search else df[df['Shop_Name'].str.contains(search, case=False)]
    
    st.dataframe(
        filtered.style
        .format({"Total_Amount": "₹{:,.0f}", "Current_Bill": "₹{:,.0f}", "Pending Balance": "₹{:,.0f}"})
        .applymap(lambda x: 'background-color: #ffcccc' if x == "Pending ❌" else None, subset=['Status']),
        use_container_width=True, hide_index=True
    )
    
    total_pending = df['Pending Balance'].sum()
    total_to_collect = df[df['Shop_Name'] != "सरकारी मीटर"]['Total_Amount'].sum()
    st.metric("कुल पेंडिंग बैलेंस", f"₹{total_pending:,.0f}")
    st.metric("इस महीने कुल वसूलना", f"₹{total_to_collect:,.0f}")

# --- 2. नई रीडिंग एंट्री ---
elif choice == "🖋️ नई रीडिंग + बिल जनरेट":
    st.header("🖋️ नई रीडिंग दर्ज करें")
    
    shop = st.selectbox("दुकान चुनें", df['Shop_Name'].tolist())
    row = df[df['Shop_Name'] == shop].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("पिछली रीडिंग", row['Prev_Reading'])
    curr = col2.number_input("Current Reading", min_value=float(row['Prev_Reading']), value=float(row['Curr_Reading']))
    rate = col3.number_input("Effective Rate (₹/unit)", value=float(row['Effective_Unit_Rate']))
    
    units = curr - row['Prev_Reading']
    bill = (units * rate) + row['Fix_Charge']
    total = bill + row['Pending Balance']
    
    st.success(f"Units: **{units}** | Current Bill: **₹{bill:,.0f}** | कुल देना: **₹{total:,.0f}**")
    
    phone = row['WhatsApp No']
    if phone != "N/A" and st.button("WhatsApp पर बिल भेजें"):
        msg = f"""हाय {shop} जी,
इस महीने का बिजली बिल:
Units इस्तेमाल: {units}
Rate: ₹{rate}
Fixed Charge: ₹{row['Fix_Charge']}
Current Bill: ₹{bill:,.0f}
पुराना बकाया: ₹{row['Pending Balance']:,.0f}
कुल जमा करना: ₹{total:,.0f}

कृपया जल्दी जमा करें। धन्यवाद! 🙏"""
        encoded = urllib.parse.quote(msg)
        whatsapp_url = f"https://wa.me/{phone}?text={encoded}"
        st.markdown(f"[📱 WhatsApp खोलें और मैसेज भेजें]({whatsapp_url})", unsafe_allow_html=True)

# --- 3. पेमेंट एंट्री (भविष्य में एक्सपैंड कर सकते हो) ---
elif choice == "💰 पेमेंट एंट्री":
    st.header("💰 पेमेंट रिसीव्ड")
    shop_pay = st.selectbox("दुकान", df['Shop_Name'].tolist())
    amt = st.number_input("मिला अमाउंट (₹)", min_value=0.0)
    mode = st.selectbox("मोड", ["Cash", "UPI", "Bank Transfer"])
    if st.button("Save Payment"):
        st.success(f"₹{amt} {mode} में रिसीव्ड! {shop_pay} का पेंडिंग अपडेट होगा।")
        # असली में यहाँ sheet.update() करो

# --- 4. सरकारी ऑडिट ---
elif choice == "📊 सरकारी ऑडिट & गैप चेक":
    st.title("📊 सरकारी बिल vs मार्केट रिकवरी")
    
    govt_row = df[df['Shop_Name'] == "सरकारी मीटर"].iloc[0]
    shops_units = df[df['Shop_Name'] != "सरकारी मीटर"]['Units_Used'].sum()
    govt_units = govt_row['Units_Used']
    gap = govt_units - shops_units
    
    col1, col2, col3 = st.columns(3)
    col1.metric("सरकारी यूनिट्स", govt_units)
    col2.metric("दुकानों से यूनिट्स", shops_units)
    col3.metric("गैप (Loss/Chori?)", gap, delta_color="inverse" if gap > 0 else "normal")
    
    total_recoverable = df[df['Shop_Name'] != "सरकारी मीटर"]['Total_Amount'].sum()
    govt_demand = govt_row['Total_Amount']  # या अलग से सरकारी बिल अमाउंट
    st.metric("मार्केट से वसूलना", f"₹{total_recoverable:,.0f}", 
              delta=f"सरकारी डिमांड से {total_recoverable - govt_demand:,.0f} कम/ज्यादा")
