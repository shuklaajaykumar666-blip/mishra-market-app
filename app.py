import streamlit as st
import pandas as pd
import plotly.express as px

# पेज सेटअप
st.set_page_config(page_title="Mishra Market", layout="wide")

# --- सुधार किया हुआ लिंक (400 Error Fix) ---
# पक्का करें कि SHEET_ID और GID के बीच में कोई स्पेस न हो
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
GID = "1626084043"

# गूगल शीट को CSV फॉर्मेट में बुलाने का सही तरीका
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60)
def load_data():
    # इस बार हम error_bad_lines का इस्तेमाल कर रहे हैं ताकि लिंक में गड़बड़ न हो
    df = pd.read_csv(CSV_URL, on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    return df.dropna(subset=['Shop_Name'])

try:
    df = load_data()
    st.title("👑 मिश्रा मार्केट बिलिंग")
    
    # मुख्य आंकड़े
    st.subheader("📊 मार्केट की स्थिति")
    df['Current_Bill'] = pd.to_numeric(df['Current_Bill'], errors='coerce').fillna(0)
    
    # चार्ट
    fig = px.bar(df, x='Shop_Name', y='Current_Bill', color='Shop_Name')
    st.plotly_chart(fig, use_container_width=True)

    # पूरी लिस्ट
    st.subheader("📋 दुकानदार सूची")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"कनेक्शन में दिक्कत है: {e}")
    st.write("कृपया चेक करें कि आपकी गूगल शीट 'Anyone with the link' पर सेट है या नहीं।")
