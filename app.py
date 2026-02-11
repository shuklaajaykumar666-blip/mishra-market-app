def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds_info = dict(st.secrets["gcp_service_account"])
    
    # चाबी को पूरी तरह साफ़ करना
    key = creds_info["private_key"]
    # अगर चाबी में पहले से BEGIN/END है तो उसे हटाकर नए सिरे से जोड़ना
    key = key.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
    key = key.replace("\\n", "\n").replace("\n", "").strip()
    
    # अब इसे सही फॉर्मेट में पैक करना
    formatted_key = f"-----BEGIN PRIVATE KEY-----\n{key}\n-----END PRIVATE KEY-----\n"
    creds_info["private_key"] = formatted_key
    
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)
