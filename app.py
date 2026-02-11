import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Mishra Market HQ", layout="wide")

# मुनीम जी का कनेक्शन सीधे 'key.json' फाइल से
def get_gspread_client():
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        # अब हम किसी 'Secrets' के चक्कर में नहीं पड़ेंगे, सीधे फाइल उठाएंगे
        creds = Credentials.from_service_account_file('key.json', scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"कनेक्शन में दिक्कत: {e}")
        return None

st.title("👑 मिश्रा मार्केट डिजिटल हेडक्वाटर")

client = get_gspread_client()
if client:
    try:
        # पक्का करें कि शीट का नाम सही है
        sheet = client.open("Mishra_Market_Data").sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        st.success("बधाई हो राजा साहब! डेटा लोड हो गया।")
        st.dataframe(df)
    except Exception as e:
        st.error(f"शीट खोलने में दिक्कत: {e}")
