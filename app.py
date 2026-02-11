import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Mishra Market HQ", layout="wide")
st.title("👑 मिश्रा मार्केट डिजिटल हेडक्वाटर")

# सबसे आसान तरीका
def connect_to_sheet():
    try:
        # हम सीधे स्ट्रीकलिट के सीक्रेट्स का इस्तेमाल करेंगे, बिना किसी छेड़छाड़ के
        creds_dict = st.secrets["gcp_service_account"]
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        
        # यहाँ 'private_key' को साफ़ करने का सबसे सरल तरीका
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"कनेक्शन एरर: {e}")
        return None

client = connect_to_sheet()

if client:
    try:
        # अपनी शीट का नाम यहाँ लिखें
        sheet = client.open("Mishra_Market_Data").sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        st.success("मुनीम जी रिकॉर्ड लेकर हाजिर हैं!")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"शीट नहीं मिल रही: {e}")
