import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

st.set_page_config(page_title="मिश्रा मार्केट", layout="wide")

# डेटा लिंक
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        # --- जादुई लाइन: सभी कॉलम के नाम से स्पेस हटाकर अंडरस्कोर लगा देगी ---
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('No', 'No')
        
        # अगर Shop_Name है तो ही आगे बढ़ें
        if 'Shop_Name' in df.columns:
            df = df.dropna(subset=['Shop_Name'])
            
            # जरूरी कॉलम जो कोड को चाहिए (अगर शीट में नाम थोड़ा अलग भी हुआ तो ये संभाल लेगा)
            # हमने 'Pending_Balance' को 'Pending_Balance' बनाने की कोशिश की है
            
            # नंबरों को सही करना
            check_cols = ['Current_Bill', 'Pending_Balance', 'Total_Amount', 'Units_Used', 'Prev_Reading', 'Curr_Reading']
            for c in check_cols:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                else:
                    # अगर कॉलम नहीं मिला तो 0 की एक नकली कॉलम बना दो ताकि एरर न आए
                    df[c] = 0
            return df
        return pd.DataFrame()
    except Exception as e:
        return str(e)

df = load_data()

if isinstance(df, pd.DataFrame) and not df.empty:
    st.title("👑 मिश्रा मार्केट - स्मार्ट बिलिंग")
    
    tab1, tab2 = st.tabs(["📊 डैशबोर्ड", "🧾 व्हाट्सएप बिल भेजें"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        
        # गणना: टोटल अमाउंट या करंट+पेंडिंग
        total_val = df['Total_Amount'].sum() if df['Total_Amount'].sum() > 0 else (df['Current_Bill'] + df['Pending_Balance']).sum()
        
        c1.metric("कुल वसूली (Total)", f"₹{total_val:,.2f}")
        c2.metric("कुल दुकानें", len(df))
        c3.metric("कुल बकाया", f"₹{df['Pending_Balance'].sum():,.2f}")

        st.divider()
        fig = px.bar(df, x='Shop_Name', y='Total_Amount', color='Total_Amount', title="दुकान वार कुल बिल")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    with tab2:
        st.subheader("दुकानदार का बिल")
        shop = st.selectbox("नाम चुनें:", df['Shop_Name'].unique())
        row = df[df['Shop_Name'] == shop].iloc[0]

        # व्हाट्सएप के लिए डेटा
        curr = row['Current_Bill']
        pend = row['Pending_Balance']
        total = row['Total_Amount'] if row['Total_Amount'] > 0 else (curr + pend)

        col_l, col_r = st.columns(2)
        with col_l:
            st.info(f"📍 दुकान: {shop}")
            st.write(f"📉 पिछली रीडिंग: {row['Prev_Reading']}")
            st.write(f"📈 नई रीडिंग: {row['Curr_Reading']}")
        with col_r:
            st.success(f"💵 इस महीने का बिल: ₹{curr}")
            st.error(f"⚠️ पुराना बकाया: ₹{pend}")
            st.warning(f"🏦 कुल देय राशि: ₹{total}")

        # संदेश
        msg = (
            f"👑 *मिश्रा मार्केट - बिजली बिल*\n\n"
            f"📍 दुकान: *{shop}*\n"
            f"🔢 यूनिट्स: {row['Units_Used']}\n"
            f"--------------------------\n"
            f"💵 माह बिल: ₹{curr}\n"
            f"⚠️ बकाया: ₹{pend}\n"
            f"💰 *कुल देय राशि: ₹{total}*\n"
            f"--------------------------\n"
            f"धन्यवाद। 🙏"
        )
        
        # WhatsApp No से स्पेस या डॉट हटाना
        phone_raw = str(row.get('WhatsApp_No', '')).split('.')[0].replace(' ', '')
        wa_url = f"https://wa.me/91{phone_raw}?text={urllib.parse.quote(msg)}"
        
        st.divider()
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366;color:white;padding:15px;border:none;border-radius:10px;width:100%;font-weight:bold;cursor:pointer;">🟢 व्हाट्सएप पर फाइनल बिल भेजें</button></a>', unsafe_allow_html=True)

else:
    st.error("डेटा लोड नहीं हो पाया।")
    st.info("💡 समाधान: अपनी गूगल शीट में 'Pending Balance' कॉलम का नाम चेक करें।")
