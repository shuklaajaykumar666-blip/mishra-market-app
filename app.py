import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Mishra Market HQ", layout="wide")

def get_gspread_client():
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        # Secrets से डेटा लेना
        creds_info = dict(st.secrets["gcp_service_account"])
        
        # राजा साहब, यहाँ असली जादू है - चाबी को साफ करना
        raw_key = creds_info["private_key"]
        # सारे \n और फालतू निशानों को ठीक करना
        clean_key = raw_key.replace("\\n", "\n")
        creds_info["private_key"] = clean_key
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"चाबी लोड नहीं हो रही: {e}")
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
    st.success("बधाई हो राजा साहब! सिस्टम चालू हो गया।")
    st.data_editor(df) # यहाँ आपकी दुकानों का डेटा दिखेगा
