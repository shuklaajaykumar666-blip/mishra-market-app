import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Mishra Market HQ", layout="wide")

def get_gspread_client():
    try:
        # यहाँ 'r' का मतलब है Raw String - ये हर एरर को खत्म कर देगा
        private_key = r"""-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCvNF4Fg+2SERpa
OdzXnJtiDBC/VDhOlLb97XcsTnR9N7gSIzM4Qr9u4qAGAYh+evWX3ZXRAqWrtVCi
Zrb1tH2Y6tR30gcBjeftIAEISk4LhvOYwar2z5zWDzobJ035YL9il5cGIyfjkjoi
apyRFpZN1GsClOuZ2gi1riwBJHH3lwtx651LZvx8b9k0NFdH+AYU6p/BCIpIkgle
fkEA3UtwbY3cBPBP5pNjQFrh6tOsjfWPFEO0T1Cx++zp2yatG51kK20WESpCOuTR
EY1YfWiaC4naub1ShBSVopKhHqnXmuoOfISBTwi81a3BsUY4vcALi9DZ3V99qIbu
SSrYFV7bAgMBAAECggEACOqksP8qg2PfcCFrEzC4hQrm0fXv+lUojaUc4De18fwj
SrkD4vnH/aqxnjH3HQjA9aj59kMo5KOQ+6g36NVLYbxBx+n7yqEgNo80aOmZ2I2r
nrsx1OcdV5TleNBNRZhzj7RLTq1SBbZBbdL4g4x0uyKeYj6V/E8pC6YA6KX5hDIp
aLzk+dHWsLfyIUhwZpSxPDDKiDcuBDXyhDbpV88k79sAqTzWUN7imRIii7Aa4Xi+
3Gzux3lNMaH0w0YE7s1pWyUTqjhPNqj8HY1XSc8b4oBufIwrcsfBA7oQISBJMG32
pUXEb7pTTKk2UEvEcbGc74Q7YPvL9Bs21P+FGHffUQKBgQDmxzXUetFUl9rJF2Bi
tGABb5OrrhtYBN8x2bgXJY426UAbU4fG1RcYFi/CQC18106GHhoBnJtXRhdZnJKU
M2Tx2vN9KgqjoDIoF7BpGpJeDzOeuX8WCijottWYyZ61EK3T9h2fIDPLAK17nXmu
p+lT89M9Hzg40sBf5jAYZqMrXQKBgQDCWkzBfnJPU8aHmdePvvPhlArcQQ1dMOwY
fcGxzzIPpDH2OXiKNk4QaWhUb8yyj5V5/qFI3e07kBVpZvYse67HH+4WwySoLUAl
K66mVAtAC04lYz0B7tHmXv/ZaVoD+HjMXiJIYSZ4gQRnprFRdDjEoZV1FnR34XdN
pe2fQxBHlwKBgQCWF/pqt3ZuDlW9c/a8O5Q1WtwwTIx8Mq73PSL96u8Tx6BqJWmp
Z+4dPFDTheoPx/jKQcmoQrLFkFCfd7XdrY95vW2fejhxMz9r0/xoX1/SzRBFq198
dh8lO8SwGnGeUbq8oNWjKM6GuWobe9AoSAz5DRvWJPfr/SYhORUOybJWAQKBgGjk
6aZJA5Ly6SSIkIIhkmj+SLpFVdwlKlexj9fStvcgLGLy867MzmcnLMrdqEH7Ira8
CfpU5NQP2K6Rhm3Nty/7eLnKSr+F5KfrIpDcrVG8iEm/fM7NQXYvcbC6nn2kHjZW
2/PqkyPYpjL3EZ6ftn/RoeOW4fdNteEvm8coH+IzAoGADP4JsZiIh5VZPc9gF/9o
Do3KAe/dbKpIjYF26NxFkTNch0z5treSLDMh/J4NU89kjYpGKsI7vAjkamJsnh/4
ofLDSyHGGW9MFtRhnkzehH2NXJxw9lgUlx1qsYN+e8TI+9ESMwZi5t4786tgpgYe
ezZfARB/tcWPffQSvht3a/xc=
-----END PRIVATE KEY-----"""

        info = {
            "type": "service_account",
            "project_id": "luminous-bond-427908-g6",
            "private_key_id": "d9ab96cd9668c744156853b19be7592c317f123c",
            "private_key": private_key,
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
        sheet = client.open("Mishra_Market_Data").sheet1
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            st.success("मुनीम जी तैनात हैं! डेटा लोड हो गया।")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("शीट मिल गई, पर अभी उसमें कोई डेटा नहीं है।")
    except Exception as e:
        st.error(f"शीट नहीं मिल रही: {e}")
