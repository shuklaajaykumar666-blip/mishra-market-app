import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- पेज सेटिंग ---
st.set_page_config(page_title="Mishra Market HQ", layout="wide")

# --- चाबी का कनेक्शन (Secrets) ---
def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    
    # राजा साहब, यहाँ हमने एक 'Filter' लगाया है जो चाबी को साफ़ करेगा
    creds_info = dict(st.secrets["gcp_service_account"])
    # \n को असली न्यू-लाइन में बदलना ज़रूरी है
    creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
    
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)

# --- डेटा लोड करना ---
def load_data():
    client = get_gspread_client()
    # अपनी शीट का नाम यहाँ लिखें
    sheet = client.open("Mishra_Market_Data").sheet1 
    data = sheet.get_all_records()
    return pd.DataFrame(data), sheet

# --- ऐप का मुख्य हिस्सा ---
st.title("👑 मिश्रा मार्केट डिजिटल हेडक्वाटर")

try:
    df, sheet = load_data()

    tab1, tab2, tab3 = st.tabs(["📊 डैशबोर्ड", "📝 रीडिंग एंट्री", "💰 पेमेंट लेजर"])

    with tab1:
        st.subheader("मार्केट की स्थिति")
        # कॉलम के नाम आपके द्वारा दिए गए नामों से मैच होने चाहिए
        total_units = df['Units_Used'].sum()
        total_collection = df['Total_Amount'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("कुल खपत (Units)", f"{total_units}")
        c2.metric("कुल वसूली लक्ष्य", f"₹{total_collection}")
        c3.metric("सरकारी बिल", "₹48,522") 

    with tab2:
        st.subheader("रीडिंग रजिस्टर (Editable)")
        # डेटा एडिटर जहाँ आप बदलाव कर सकते हैं
        edited_df = st.data_editor(df, num_rows="dynamic", key="data_editor")
        
        if st.button("शीट में डेटा सेव करें"):
            # शीट अपडेट करने का तरीका
            sheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
            st.success("डेटा पक्का हो गया, राजा साहब!")

    with tab3:
        st.subheader("दुकानदार का हिसाब")
        shop = st.selectbox("दुकान चुनें", df['Shop_Name'].unique())
        shop_data = df[df['Shop_Name'] == shop].iloc[0]
        
        st.write(f"### {shop} का बिल")
        st.write(f"पुरानी रीडिंग: {shop_data['Prev_Reading']}")
        st.write(f"नई रीडिंग: {shop_data['Curr_Reading']}")
        st.write(f"**कुल बकाया: ₹{shop_data['Total_Amount']}**")
        
        if st.button("WhatsApp बिल भेजें"):
            whatsapp_no = str(shop_data['WhatsApp No'])
            message = f"प्रणाम, {shop} का बिजली बिल: {shop_data['Total_Amount']} रुपये। नई रीडिंग: {shop_data['Curr_Reading']}"
            link = f"https://wa.me/{whatsapp_no}?text={message.replace(' ', '%20')}"
            st.markdown(f"[यहाँ क्लिक करके WhatsApp भेजें]({link})")

except Exception as e:
    st.error(f"अभी कनेक्शन में दिक्कत है। कृपया Secrets चेक करें।")
    st.info(f"तकनीकी एरर: {e}")
