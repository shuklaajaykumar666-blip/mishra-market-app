import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Mishra Market HQ", layout="wide")

def get_gspread_client():
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds_info = dict(st.secrets["gcp_service_account"])
        
        # चाबी की मरम्मत (Repairing the Key)
        key = creds_info["private_key"].replace("\\n", "\n")
        
        # पक्का करना कि BEGIN और END लाइन्स सही हैं
        if "-----BEGIN PRIVATE KEY-----" not in key:
            key = f"-----BEGIN PRIVATE KEY-----\n{key}\n-----END PRIVATE KEY-----\n"
            
        creds_info["private_key"] = key
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"चाबी में अभी भी दिक्कत है: {e}")
        return None

def load_data():
    client = get_gspread_client()
    if client:
        try:
            # शीट का नाम पक्का Mishra_Market_Data होना चाहिए
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
