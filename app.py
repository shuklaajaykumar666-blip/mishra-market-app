import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import webbrowser
import os

# --- Google Sheet Setup (अपना Credentials JSON और Sheet ID डालो) ---
# 1. Google Cloud से Service Account बनाओ, JSON डाउनलोड करो।
# 2. लोकल में: credentials.json रखो।
# 3. Streamlit Cloud/Heroku पर: Secrets में डालो (st.secrets["gcp_service_account"] = {...})
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gsheet_client():
    # लोकल टेस्ट के लिए JSON फाइल
    creds_dict = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----",
        "client_email": "your-service-account-email@project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "your-cert-url"
    }
    # ऊपर वाला creds_dict अपना डालो। Streamlit Cloud में st.secrets से लोड करो।
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
    client = gspread.authorize(creds)
    return client

# अपना Google Sheet ID डालो (URL से कॉपी करो)
SHEET_ID = "1YourSheetIDHere_ReplaceWithRealID"  # <-- यहां अपना Sheet ID पेस्ट करो

client = get_gsheet_client()
sheet = client.open_by_key(SHEET_ID)

# --- Helper Functions ---
def load_data(tab_name):
    ws = sheet.worksheet(tab_name)
    data = ws.get_all_records()
    df = pd.DataFrame(data)
    return df, ws

def update_cell(ws, row, col, value):
    ws.update_cell(row, col, value)

def append_row(ws, row_data):
    ws.append_row(row_data)

# --- ऐप सेटिंग ---
st.set_page_config(page_title="मिश्रा मार्केट डिजिटल मुनीम 👑", layout="wide")
st.title("मिश्रा मार्केट - जीरो लॉस रिकवरी सिस्टम 🚀")

# --- साइडबार मेनू ---
st.sidebar.title("👑 मेनू")
choice = st.sidebar.radio("चुनें", [
    "📊 डैशबोर्ड",
    "🖋️ रीडिंग एंट्री & बिल",
    "💰 पेमेंट एंट्री",
    "🗓️ महीना बंद (Month Close)",
    "📄 PDF हिस्ट्री",
    "🔍 सरकारी बिल & गैप ट्रैकर"
])

# --- 1. डैशबोर्ड ---
if choice == "📊 डैशबोर्ड":
    st.header("एक नजर में सब")
    df_shop, ws_shop = load_data("SHOP_DATA")
    if not df_shop.empty:
        # डायनामिक शॉप्स काउंट
        num_shops = len(df_shop[df_shop['Shop_Name'] != "सरकारी मीटर"])
        st.metric("कुल दुकानें (Dynamic)", num_shops)
        
        # कुल पेंडिंग, वसूली, आदि
        total_pending = df_shop['Pending_Amount'].astype(float).sum()
        total_payable = df_shop['Total_Payable_Amount'].astype(float).sum()
        st.metric("कुल पेंडिंग", f"₹{total_pending:,.0f}", delta_color="inverse")
        st.metric("इस महीने कुल वसूलना", f"₹{total_payable:,.0f}")
        
        # स्टेटस के साथ टेबल (ग्रीन/रेड)
        styled = df_shop.style.applymap(lambda x: 'background-color: green' if x == "Paid ✅" else 'background-color: red' if x == "Pending ❌" else None, subset=['Status'])
        st.dataframe(styled, use_container_width=True)

# --- 2. रीडिंग एंट्री & बिल ---
elif choice == "🖋️ रीडिंग एंट्री & बिल":
    st.header("Current Reading डालें → बिल तैयार")
    df_shop, ws_shop = load_data("SHOP_DATA")
    shop_list = df_shop['Shop_Name'].tolist()
    shop = st.selectbox("दुकान चुनें (Dynamic List)", shop_list)
    
    if shop:
        row = df_shop[df_shop['Shop_Name'] == shop].index[0] + 2  # gspread 1-indexed + header
        prev = float(df_shop.loc[df_shop['Shop_Name'] == shop, 'Prev_Reading'].values[0])
        rate = float(df_shop.loc[df_shop['Shop_Name'] == shop, 'Effective_Unit_Rate'].values[0])
        fixed = float(df_shop.loc[df_shop['Shop_Name'] == shop, 'Fixed_Charge'].values[0])
        pending = float(df_shop.loc[df_shop['Shop_Name'] == shop, 'Pending_Amount'].values[0])
        
        curr = st.number_input("Current Reading", min_value=prev)
        
        if st.button("बिल कैलकुलेट & सेव"):
            if curr > prev:
                units = curr - prev
                curr_bill = (units * rate) + fixed
                total = round(curr_bill + pending)
                
                # शीट अपडेट
                update_cell(ws_shop, row, df_shop.columns.get_loc('Curr_Reading') + 1, curr)
                update_cell(ws_shop, row, df_shop.columns.get_loc('Units_Used') + 1, units)
                update_cell(ws_shop, row, df_shop.columns.get_loc('Current_Bill') + 1, curr_bill)
                update_cell(ws_shop, row, df_shop.columns.get_loc('Total_Payable_Amount') + 1, total)
                
                st.success(f"Units: {units} | Current Bill: ₹{curr_bill:,.0f} | कुल: ₹{total:,.0f}")
                
                # WhatsApp बिल
                phone = df_shop.loc[df_shop['Shop_Name'] == shop, 'WhatsApp No'].values[0]
                msg = f"नमस्ते {shop} जी,\nUnits: {units}\nRate: ₹{rate}\nFixed: ₹{fixed}\nCurrent Bill: ₹{curr_bill}\nPending: ₹{pending}\nकुल: ₹{total}\nधन्यवाद!"
                url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
                if st.button("WhatsApp भेजें"):
                    webbrowser.open(url)

# --- 3. पेमेंट एंट्री ---
elif choice == "💰 पेमेंट एंट्री":
    st.header("पेमेंट रिसीव्ड")
    df_shop, ws_shop = load_data("SHOP_DATA")
    df_ledger, ws_ledger = load_data("PAYMENT_LEDGER")
    
    shop = st.selectbox("दुकान", df_shop['Shop_Name'].tolist())
    amount = st.number_input("मिला अमाउंट", min_value=0.0)
    mode = st.selectbox("मोड", ["Cash", "Online"])
    date = datetime.now().strftime("%Y-%m-%d")
    
    if st.button("Save Payment"):
        row = df_shop[df_shop['Shop_Name'] == shop].index[0] + 2
        total_due = float(df_shop.loc[df_shop['Shop_Name'] == shop, 'Total_Payable_Amount'].values[0])
        new_pending = total_due - amount
        
        # अपडेट SHOP_DATA
        update_cell(ws_shop, row, df_shop.columns.get_loc('Pending_Amount') + 1, new_pending)
        status = "Paid ✅" if new_pending <= 0 else "Pending ❌"
        update_cell(ws_shop, row, df_shop.columns.get_loc('Status') + 1, status)
        
        # Ledger में ऐड
        append_row(ws_ledger, [shop, amount, mode, date, new_pending])
        
        st.success(f"पेमेंट सेव! नया पेंडिंग: ₹{new_pending:,.0f}")
        
        # Receipt WhatsApp
        phone = df_shop.loc[df_shop['Shop_Name'] == shop, 'WhatsApp No'].values[0]
        msg = f"धन्यवाद {shop} जी! ₹{amount} ({mode}) मिला। बाकी: ₹{new_pending}\nतारीख: {date}"
        url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
        if st.button("रसीद भेजें"):
            webbrowser.open(url)

# --- 4. महीना बंद ---
elif choice == "🗓️ महीना बंद (Month Close)":
    st.header("महीना बंद करें - Careful!")
    df_shop, ws_shop = load_data("SHOP_DATA")
    df_history, ws_history = load_data("BILL_HISTORY")
    
    if st.button("Month Close & Carry Forward"):
        for i, row_data in df_shop.iterrows():
            if row_data['Shop_Name'] != "सरकारी मीटर":
                # History में सेव
                append_row(ws_history, [row_data['Shop_Name'], datetime.now().strftime("%Y-%m"), row_data['Prev_Reading'], row_data['Curr_Reading'], row_data['Units_Used'], row_data['Current_Bill'], row_data['Pending_Amount'], row_data['Total_Payable_Amount']])
                
                # Carry Forward: Curr → Prev, क्लियर Curr, Pending रहता है
                shop_row = i + 2
                update_cell(ws_shop, shop_row, df_shop.columns.get_loc('Prev_Reading') + 1, row_data['Curr_Reading'])
                update_cell(ws_shop, shop_row, df_shop.columns.get_loc('Curr_Reading') + 1, 0)
                update_cell(ws_shop, shop_row, df_shop.columns.get_loc('Units_Used') + 1, 0)
                update_cell(ws_shop, shop_row, df_shop.columns.get_loc('Current_Bill') + 1, 0)
        
        st.success("महीना बंद! History सेव, नेक्स्ट मंथ रेडी।")

# --- 5. PDF हिस्ट्री ---
elif choice == "📄 PDF हिस्ट्री":
    st.header("PDF Ledger जनरेट")
    df_shop, _ = load_data("SHOP_DATA")
    df_history, _ = load_data("BILL_HISTORY")
    
    shop = st.selectbox("दुकान", df_shop['Shop_Name'].tolist())
    
    if st.button("PDF बनाएं"):
        hist = df_history[df_history['Shop_Name'] == shop]
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, f"{shop} का पूरा हिस्ट्री")
        y = 700
        for _, r in hist.iterrows():
            c.drawString(100, y, f"{r['Month']}: Units {r['Units_Used']}, Bill ₹{r['Current_Bill']}, Pending ₹{r['Pending_Amount']}")
            y -= 20
        c.save()
        buffer.seek(0)
        st.download_button("PDF डाउनलोड", buffer, f"{shop}_history.pdf", "application/pdf")

# --- 6. सरकारी बिल & गैप ट्रैकर ---
elif choice == "🔍 सरकारी बिल & गैप ट्रैकर":
    st.header("सरकारी बिल ट्रैकर")
    df_govt, ws_govt = load_data("GOVT_BILL_DATA")
    
    # सरकारी डेटा इनपुट
    govt_units = st.number_input("सरकारी यूनिट्स")
    govt_amount = st.number_input("सरकारी बिल अमाउंट")
    paid_date = st.date_input("पेड डेट")
    paid_mode = st.selectbox("पेड मोड", ["Cash", "Online"])
    
    if st.button("Govt Bill Save"):
        append_row(ws_govt, [datetime.now().strftime("%Y-%m"), govt_units, govt_amount, paid_date, paid_mode])
        st.success("सेव!")
    
    # गैप चेक
    df_shop, _ = load_data("SHOP_DATA")
    shop_units = df_shop['Units_Used'].astype(float).sum()
    gap = govt_units - shop_units
    st.metric("गैप (चोरी/लॉस)", gap, delta_color="inverse")
    if gap > 0:
        st.error("अलर्ट: गैप है! चेक करें।")

st.sidebar.info("Developed by Grok | सभी डेटा गूगल शीट से लाइव। सुरक्षित & ट्रांसपेरेंट 👑")
