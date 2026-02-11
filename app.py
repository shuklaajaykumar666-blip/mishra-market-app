import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- पेज सेटिंग ---
st.set_page_config(page_title="Mishra Market HQ", layout="wide")

# --- चाबी को साफ़ और कनेक्ट करने का फंक्शन ---
def get_gspread_client():
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        
        # Secrets से डेटा उठाना
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # चाबी की सफाई (Cleaning the PEM Key)
        raw_key = creds_dict["private_key"]
        if "-----BEGIN PRIVATE KEY-----" not in raw_key:
            # अगर चाबी में BEGIN/END नहीं है तो उसे जोड़ना
            clean_key = raw_key.replace("\\n", "\n").strip()
            formatted_key = f"-----BEGIN PRIVATE KEY-----\n{clean_key}\n-----END PRIVATE KEY-----\n"
            creds_dict["private_key"] = formatted_key
        else:
            # अगर BEGIN/END है, तो सिर्फ \n को ठीक करना
            creds_dict["private_key"] = raw_key.replace("\\n", "\n")

        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"चाबी (Secrets) में गड़बड़ है: {e}")
        return None

# --- डेटा लोड करना ---
def load_data():
    client = get_gspread_client()
    if client:
        try:
            # शीट का नाम पक्का Mishra_Market_Data होना चाहिए
            spreadsheet = client.open("Mishra_Market_Data")
            sheet = spreadsheet.sheet1
            data = sheet.get_all_records()
            return pd.DataFrame(data), sheet
        except Exception as e:
            st.error(f"शीट नहीं खुल रही: {e}")
            st.info("चेक करें: क्या आपने 'mishra-market-app@...' ईमेल को शीट में Editor बनाया है?")
            return None, None
    return None, None

# --- मुख्य ऐप ---
st.title("👑 मिश्रा मार्केट डिजिटल हेडक्वाटर")

try:
    df, sheet = load_data()

    if df is not None and not df.empty:
        st.success("डेटा सफलतापूर्वक लोड हो गया है!")
        
        tab1, tab2, tab3 = st.tabs(["📊 डैशबोर्ड", "📝 रीडिंग एंट्री", "💰 पेमेंट लेजर"])

        with tab1:
            st.subheader("मार्केट की स्थिति")
            c1, c2, c3 = st.columns(3)
            # कॉलम के नाम वही होने चाहिए जो आपकी शीट में हैं
            try:
                c1.metric("कुल खपत (Units)", f"{df['Units_Used'].sum()}")
                c2.metric("कुल वसूली लक्ष्य", f"₹{df['Total_Amount'].sum()}")
                c3.metric("सरकारी बिल", "₹48,522")
            except:
                st.warning("शीट के कॉलम नाम चेक करें (Shop_Name, Units_Used, etc.)")

        with tab2:
            st.subheader("रीडिंग रजिस्टर")
            edited_df = st.data_editor(df, num_rows="dynamic", key="data_editor")
            if st.button("शीट में डेटा सेव करें"):
                # पूरी शीट अपडेट करना
                sheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
                st.success("डेटा पक्का हो गया, राजा साहब!")

        with tab3:
            st.subheader("दुकानदार का हिसाब")
            shop = st.selectbox("दुकान चुनें", df['Shop_Name'].unique())
            shop_data = df[df['Shop_Name'] == shop].iloc[0]
            st.write(f"### {shop} का हिसाब")
            st.json(shop_data.to_dict()) # सारा डेटा यहाँ दिखेगा

    elif df is not None and df.empty:
        st.warning("शीट तो मिल गई, पर उसमें कोई डेटा नहीं है।")

except Exception as e:
    st.error(f"ऐप चलाने में दिक्कत आई: {e}")
