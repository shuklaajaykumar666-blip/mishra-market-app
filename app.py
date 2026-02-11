import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Mishra Market HQ", layout="wide")
st.title("👑 मिश्रा मार्केट डिजिटल हेडक्वाटर")

def connect_to_sheet():
    try:
        # Secrets की एक कॉपी बनाना
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        
        # चाबी की सफाई
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        # यहाँ सुधार किया गया है: 'creds_info=' हटाकर सीधे डेटा भेजा गया है
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"कनेक्शन एरर: {e}")
        return None

client = connect_to_sheet()

if client:
    try:
        # शीट का नाम पक्का चेक करें
        sheet = client.open("Mishra_Market_Data").sheet1
        data = sheet.get_all_records()
        
        if data:
            df = pd.DataFrame(data)
            st.success("मुनीम जी तैनात हैं! डेटा लोड हो गया।")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("शीट मिल गई, पर उसमें कोई डेटा नहीं है।")
            
    except Exception as e:
        st.error(f"शीट खोलने में दिक्कत: {e}")
