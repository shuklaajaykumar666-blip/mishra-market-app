import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Mishra Market HQ", layout="wide")

# मुनीम जी का पक्का बहीखाता (Direct Dictionary)
def get_gspread_client():
    try:
        # यहाँ हमने चाबी को सीधे डिक्शनरी में डाल दिया है ताकि JSON का झंझट न रहे
        info = {
            "type": "service_account",
            "project_id": "luminous-bond-427908-g6",
            "private_key_id": "d9ab96cd9668c744156853b19be7592c317f123c",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCvNF4Fg+2SERpa\nOdzXnJtiDBC/VDhOlLb97XcsTnR9N7gSIzM4Qr9u4qAGAYh+evWX3ZXRAqWrtVCi\nZrb1tH2Y6tR30gcBjeftIAEISk4LhvOYwar2z5zWDzobJ035YL9il5cGIyfjkjoi\napyRFpZN1GsClOuZ2gi1riwBJHH3lwtx651LZvx8b9k0NFdH+AYU6p/BCIpIkgle\nfkEA3UtwbY3cBPBP5pNjQFrh6tOsjfWPFEO0T1Cx++zp2yatG51kK20WESpCOuTR\nEY1YfWiaC4naub1ShBSVopKhHqnXmuoOfISBTwi81a3BsUY4vcALi9DZ3V99qIbu\nSSrYFV7bAgMBAAECggEACOqksP8qg2PfcCFrEzC4hQrm0fXv+lUojaUc4De18fwj\nSrkD4vnH/aqxnjH3HQjA9aj59kMo5KOQ+6g36NVLYbxBx+n7yqEgNo80aOmZ2I2r\nrrsx1OcdV5TleNBNRZhzj7RLTq1SBbZBbdL4g4x0uyKeYj6V/E8pC6YA6KX5hDIp\naLzk+dHWsLfyIUhwZpSxPDDKiDcuBDXyhDbpV88k79sAqTzWUN7imRIii7Aa4Xi+\n3Gzux3lNMaH0w0YE7s1pWyUTqjhPNqj8HY1XSc8b4oBufIwrcsfBA7oQISBJMG32\npUXEb7pTTKk2UEvEcbGc74Q7YPvL9Bs21P+FGHffUQKBgQDmxzXUetFUl9rJF2Bi\ntGABb5OrrhtYBN8x2bgXJY426UAbU4fG1RcYFi/CQC18106GHhoBnJtXRhdZnJKU\nM2Tx2vN9KgqjoDIoF7BpGpJeDzOeuX8WCijottWYyZ61EK3T9h2fIDPLAK17nXmu\np+lT89M9Hzg40sBf5jAYZqMrXQKBgQDCWkzBfnJPU8aHmdePvvPhlArcQQ1dMOwY\fcGxzzIPpDH2OXiKNk4QaWhUb8yyj5V5/qFI3e07kBVpZvYse67HH+4WwySoLUAl\nK66mVAtAC04lYz0B7tHmXv/ZaVoD+HjMXiJIYSZ4gQRnprFRdDjEoZV1FnR34XdN\pe2fQxBHlwKBgQCWF/pqt3ZuDlW9c/a8O5Q1WtwwTIx8Mq73PSL96u8Tx6BqJWmp\nZ+4dPFDTheoPx/jKQcmoQrLFkFCfd7XdrY95vW2fejhxMz9r0/xoX1/SzRBFq198\ndh8lO8SwGnGeUbq8oNWjKM6GuWobe9AoSAz5DRvWJPfr/SYhORUOybJWAQKBgGjk\n6aZJA5Ly6SSIkIIhkmj+SLpFVdwlKlexj9fStvcgLGLy867MzmcnLMrdqEH7Ira8\nCfpU5NQP2K6Rhm3Nty/7eLnKSr+F5KfrIpDcrVG8iEm/fM7NQXYvcbC6nn2kHjZW\n2/PqkyPYpjL3EZ6ftn/RoeOW4fdNteEvm8coH+IzAoGADP4JsZiIh5VZPc9gF/9o\ Do3KAe/dbKpIjYF26NxFkTNch0z5treSLDMh/J4NU89kjYpGKsI7vAjkamJsnh/4\nofLDSyHGGW9MFtRhnkzehH2NXJxw9lgUlx1qsYN+e8TI+9ESMwZi5t4786tgpgYe\nezZfARB/tcWPffQSvht3a/xc=\n-----END PRIVATE KEY-----\n",
            "client_email": "mishra-market-app@luminous-bond-427908-g6.iam.gserviceaccount.com",
            "client_id": "112554782070285781791",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/mishra-market-app%40luminous-bond-427908-g6.iam.gserviceaccount.com"
        }
        
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"चाबी में दिक्कत: {e}")
        return None

st.title("👑 मिश्रा मार्केट डिजिटल हेडक्वाटर")

client = get_gspread_client()
if client:
    try:
        # शीट का नाम पक्का चेक करें
        sheet = client.open("Mishra_Market_Data").sheet1
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            st.success("बधाई हो राजा साहब! मार्केट का डेटा लोड हो गया।")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("शीट मिल गई, पर अभी उसमें कोई डेटा नहीं है।")
    except Exception as e:
        st.error(f"शीट नहीं मिल रही: {e}")
        st.info("चेक करें कि गूगल शीट का नाम 'Mishra_Market_Data' ही है।")
