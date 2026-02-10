import streamlit as st
import pandas as pd
import urllib.parse
import webbrowser
import matplotlib.pyplot as plt
import io

# आपका CSV लिंक (डेटा पढ़ने के लिए)
CSV_URL = "https://docs.google.com/spreadsheets/d/19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo/export?format=csv&gid=0"

# Sheet Edit लिंक (Entry के लिए)
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo/edit"

@st.cache_data(ttl=300)
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()

st.set_page_config(page_title="मिश्रा मार्केट मुनीम 👑", layout="wide")
st.title("👑 मिश्रा मार्केट - ब्रिलियंट डिजिटल मुनीम")
st.caption("महीने में 1 बार यूज • लॉजिक से कमाल • सब कुछ Sheet में सुरक्षित")

choice = st.sidebar.radio("मेनू चुनो", [
    "🏠 ब्रिलियंट डैशबोर्ड",
    "🖋️ रीडिंग + बिल भेजो",
    "💰 पेमेंट + रसीद",
    "📜 रिकॉर्ड भेजो"
])

if choice == "🏠 ब्रिलियंट डैशबोर्ड":
    st.header("एक नजर में पूरी कहानी")
    
    # लॉजिक से कुल कैलकुलेशन
    total_pending = df["Pending_Amount"].astype(float).sum()
    total_payable = df["Total_Payable_Amount"].astype(float).sum()
    gov_units = df[df["Shop_Name"] == "सरकारी मीटर"]["Units_Used"].values[0] if "सरकारी मीटर" in df["Shop_Name"].values else 0
    shop_units = df[df["Shop_Name"] != "सरकारी मीटर"]["Units_Used"].astype(float).sum()
    gap = gov_units - shop_units
    
    col1, col2, col3 = st.columns(3)
    col1.metric("कुल पेंडिंग", f"₹{total_pending:,.0f}", delta_color="inverse")
    col2.metric("कुल वसूलना", f"₹{total_payable:,.0f}")
    col3.metric("गैप (चोरी/लॉस)", gap, delta_color="inverse" if gap > 0 else "normal")
    
    # माइंड यूज: gov vs शॉप चार्ट (कहानी समझाने के लिए)
    st.subheader("gov vs शॉप यूनिट्स चार्ट")
    fig, ax = plt.subplots()
    labels = ['gov Units', 'शॉप Units']
    values = [gov_units, shop_units]
    ax.bar(labels, values, color=['blue', 'green'])
    ax.set_ylabel('Units')
    buf = io.BytesIO()
    fig.save(fig, format="png")
    buf.seek(0)
    st.image(buf)

    # दुकानों की लिस्ट (कलर के साथ)
    def color_status(val):
        if 'Paid' in str(val):
            return 'background-color: green; color: white'
        elif 'Pending' in str(val):
            return 'background-color: red; color: white'
        else:
            return 'background-color: yellow; color: black'

    styled_df = df.style.format({
        "Total_Payable_Amount": "₹{:,.0f}",
        "Pending_Amount": "₹{:,.0f}",
        "Current_Bill": "₹{:,.0f}"
    }).applymap(color_status, subset=['Status'])

    st.subheader("दुकानों का डिटेल")
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

elif choice == "🖋️ रीडिंग + बिल भेजो":
    # आपका बाकी कोड यहाँ (पिछले मैसेज से कॉपी कर लो)

# बाकी सेक्शन भी पिछले मैसेज से ले लो, और डैशबोर्ड वाला ये नया रख लो

st.sidebar.info("महीने में 1 बार यूज • ब्रिलियंट लॉजिक से कमाल 👑")
