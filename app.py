import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import re

st.set_page_config(page_title="Mishra Market HQ", layout="wide")

def get_gspread_client():
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds_info = dict(st.secrets["gcp_service_account"])
        
        # राजा साहब, यहाँ हम चाबी की 'सर्जरी' करेंगे ताकि एरर न आए
        raw_key = creds_info["private_key"]
        
        # सिर्फ ज़रूरी हिस्सा (Base64) निकालना
        # BEGIN और END के बीच का मसाला साफ़ करना
        if "-----BEGIN PRIVATE KEY-----" in raw_key:
            raw_key = raw_key.split("-----BEGIN PRIVATE KEY-----")[1]
        if "-----END PRIVATE KEY-----" in raw_key:
            raw_key = raw_key.split("-----END PRIVATE KEY-----")[0]
            
        # हर तरह का स्पेस, न्यू-लाइन और कचरा हटाना
        clean_key_body = re.sub(r'\s+', '', raw_key).strip()
        
        # अब इसे मशीन के समझने लायक सही साफ़-सुथरे फॉर्मेट में जोड़ना
        formatted_key = f"-----BEGIN PRIVATE KEY-----\n{clean_key_body}\n-----END PRIVATE KEY-----\n"
        creds_info["private_key"] = formatted_key
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"चाबी लोड करने में दिक्कत: {e}")
        return None

def load_data():
    client = get_gspread_client()
    if client:
        try:
            # शीट का नाम पक्का चेक करें
            sheet = client.open("Mishra_Market_Data").sheet1
            data = sheet.get_all_records()
            return pd.DataFrame(data), sheet
        except Exception as e:
            st.error(f"शीट नहीं मिल रही: {e}")
    return None, None

st.title("👑 मिश्रा मार्केट डिजिटल हेडक्वाटर")

df, sheet = load_data()

if df is not None:
    st.success("मुनीम जी हाजिर हैं! डेटा लोड हो गया।")
    st.data_editor(df, use_container_width=True)
