import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- पेज सेटिंग ---
st.set_page_config(page_title="Mishra Market HQ", layout="wide")

# --- चाबी चेक और कनेक्शन ---
def get_gspread_client():
    try:
        # पक्का करें कि Secrets में 'gcp_service_account' नाम सही है
        if "gcp_service_account" not in st.secrets:
            st.error("Secrets में 'gcp_service_account' नहीं मिला!")
            return None
            
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds_info = dict(st.secrets["gcp_service_account"])
        
        # चाबी का फॉर्मेट सुधारना
        key = creds_info["private_key"].replace("\\n", "\n")
        if "-----BEGIN PRIVATE KEY-----" not in key:
            key = f"-----BEGIN PRIVATE KEY-----\n{key.strip()}\n-----END PRIVATE KEY-----\n"
        creds_info["private_key"] = key
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"कन्फ़िगरेशन में त्रुटि: {e}")
        return None

# --- डेटा लोड करना ---
def load_data():
    client = get_gspread_client()
    if client:
        try:
            # अपनी गूगल शीट का नाम यहाँ बिल्कुल सही लिखें
            sheet_name = "Mishra_Market_Data" 
            spreadsheet = client.open(sheet_name)
            sheet = spreadsheet.sheet1
            data = sheet.get_all_records()
            return pd.DataFrame(data), sheet
        except gspread.exceptions.SpreadsheetNotFound:
            st.error(f"'{sheet_name}' नाम की शीट नहीं मिली! कृपया नाम चेक करें।")
            return None, None
        except Exception as e:
            st.error(f"डेटा लोड नहीं हो सका: {e}")
            return None, None
    return None, None

# --- मुख्य ऐप इंटरफेस ---
st.title("👑 मिश्रा मार्केट डिजिटल हेडक्वाटर")

# लोडिंग इंडिकेटर
with st.spinner('मुनीम जी रिकॉर्ड ला रहे हैं...'):
    df, sheet = load_data()

if df is not None:
    if not df.empty:
        st.success(f"कुल {len(df)} दुकानों का डेटा मिल गया!")
        
        # टैब्स बनाना
        tab1, tab2 = st.tabs(["📊 मुख्य डैशबोर्ड", "📝 रीडिंग अपडेट"])
        
        with tab1:
            st.dataframe(df, use_container_width=True)
            
        with tab2:
            st.info("नीचे टेबल में रीडिंग बदलें और सेव बटन दबाएँ।")
            edited_df = st.data_editor(df, num_rows="dynamic")
            if st.button("Google Sheet में सेव करें"):
                try:
                    sheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
                    st.success("डेटा शीट में अपडेट हो गया!")
                except Exception as e:
                    st.error(f"सेव करने में दिक्कत: {e}")
    else:
        st.warning("शीट मिल गई है, लेकिन उसमें कोई डेटा नहीं है।")
