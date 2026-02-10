import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# --- पेज सेटिंग ---
st.set_page_config(page_title="मिश्रा मार्केट - बिलिंग", layout="wide")
st.title("👑 मिश्रा मार्केट - स्मार्ट डैशबोर्ड")

# आपकी शीट की ID और GID
SHEET_ID = "19UmwSuKigMDdSRsVMZOVjIZAsvrqOePwcqHuP7N3qHo"
GID = "1626084043" 
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=['Shop_Name'])
        # नंबर वाले कॉलम्स को साफ़ करना
        for col in ['Current_Bill', 'Units_Used', 'Pending_Balance', 'Prev_Reading', 'Curr_Reading']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- ऊपर की पट्टी (Top Metrics) ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("कुल मार्केट बिल", f"₹{df['Current_Bill'].sum():,.2f}")
    with m2:
        st.metric("कुल बकाया राशि", f"₹{df['Pending_Balance'].sum():,.2f}", delta_color="inverse")
    with m3:
        st.metric("कुल खपत (Units)", f"{int(df['Units_Used'].sum())}")
    with m4:
        st.metric("कुल दुकानें", len(df))

    st.divider()

    # --- साइडबार मेन्यू ---
    st.sidebar.header("कंट्रोल पैनल")
    view_choice = st.sidebar.radio("क्या देखना है?", ["📊 डैशबोर्ड", "🧾 दुकान का बिल निकालें", "📋 पूरी लिस्ट"])

    if view_choice == "📊 डैशबोर्ड":
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("📈 टॉप 10 बिल (दुकान वार)")
            top_10 = df.nlargest(10, 'Current_Bill')
            fig1 = px.bar(top_10, x='Shop_Name', y='Current_Bill', color='Current_Bill', text_auto='.2s')
            st.plotly_chart(fig1, use_container_width=True)
        with col_b:
            st.subheader("🥧 बकाया राशि का हिस्सा")
            fig2 = px.pie(df[df['Pending_Balance'] > 0], values='Pending_Balance', names='Shop_Name', hole=0.3)
            st.plotly_chart(fig2, use_container_width=True)

    elif view_choice == "🧾 दुकान का बिल निकालें":
        st.subheader("🔍 दुकान चुनें")
        selected_shop = st.selectbox("दुकानदार का नाम:", df['Shop_Name'].unique())
        row = df[df['Shop_Name'] == selected_shop].iloc[0]

        # बिल की सुंदर रसीद
        st.info(f"📍 दुकान: **{selected_shop}**")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write(f"📉 पिछली रीडिंग: **{row['Prev_Reading']}**")
            st.write(f"📈 नई रीडिंग: **{row['Curr_Reading']}**")
        with c2:
            st.write(f"⚡ कुल यूनिट: **{row['Units_Used']}**")
            st.write(f"💰 रेट: ₹**{row.get('Effective_Unit_Rate', 0)}**")
        with c3:
            total_pay = row['Current_Bill'] + row['Pending_Balance']
            st.success(f"💵 इस महीने का बिल: ₹**{row['Current_Bill']}**")
            st.error(f"⚠️ बकाया: ₹**{row['Pending_Balance']}**")
            st.warning(f"🏦 कुल जमा करना है: ₹**{total_pay}**")

        # --- व्हाट्सएप बटन ---
        msg = f"नमस्ते {selected_shop},\nआपका मिश्रा मार्केट का बिल तैयार है:\n⚡ यूनिट: {row['Units_Used']}\n💵 इस महीने का बिल: ₹{row['Current_Bill']}\n⚠️ पुराना बकाया: ₹{row['Pending_Balance']}\n🏦 कुल राशि: ₹{total_pay}\nधन्यवाद।"
        encoded_msg = urllib.parse.quote(msg)
        wa_url = f"https://wa.me/91{row['WhatsApp_No']}?text={encoded_msg}"
        
        st.markdown(f'''
            <a href="{wa_url}" target="_blank">
                <button style="background-color: #25D366; color: white; padding: 10px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px;">
                    🟢 WhatsApp पर बिल भेजें
                </button>
            </a>
            ''', unsafe_allow_html=True)

    elif view_choice == "📋 पूरी लिस्ट":
        st.subheader("मार्केट की पूरी रिपोर्ट")
        st.dataframe(df, use_container_width=True)

else:
    st.error("डेटा लोड नहीं हुआ! कृपया अपनी गूगल शीट चेक करें।")

st.sidebar.markdown("---")
st.sidebar.info("मिश्रा मार्केट बिलिंग सिस्टम v2.0")
