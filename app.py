import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import re

st.set_page_config(page_title="Mishra Market HQ", layout="wide")

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    
    # Secrets से डेटा लेना
    creds_info = dict(st.secrets["gcp_service_account"])
    
    # चाबी को साफ़ करने का "ब्रह्मास्त्र"
    raw_key = creds_info["private_key"]
    # यह लाइन फालतू स्पेस और गलत निशानों को हटा देगी
    clean_key = raw_key.replace("\\n", "\n").replace(" ", "").replace("\n", "NEWLINE")
    clean_key = clean_key.replace("BEGINPRIVATEKEY", "-----BEGIN PRIVATE KEY-----\n")
    clean_key = clean_key.replace("ENDPRIVATEKEY", "\n-----END PRIVATE KEY-----")
    clean_key = clean_key.replace("NEWLINE", "\n")
    
    # साफ़ की हुई चाबी वापस डालना
    creds_info["private_key"] = clean_key
    
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)

def load_data():
    client = get_gspread_client()
    sheet = client.open("Mishra_Market_Data").sheet1 
    data = sheet.get_all_records()
    return pd.DataFrame(data), sheet

st.title("👑 मिश्रा मार्केट डिजिटल हेडक्वाटर")

try:
    df, sheet = load_data()
    st.success("कनेक्शन कामयाब! डेटा लोड हो गया।")
    st.dataframe(df) # टेस्टिंग के लिए डेटा देखना
except Exception as e:
    st.error(f"अभी भी दिक्कत है।")
    st.info(f"तकनीकी एरर: {e}")
