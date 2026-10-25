import streamlit as st
import pandas as pd

st.set_page_config(page_title="ESP32 Dashboard", layout="wide")
st.title("ESP32 Sensor Dashboard")

# Load data dengan cache dan TTL agar otomatis terupdate
@st.cache_data(ttl=2) 
def load_data():
    try:
        df = pd.read_csv("data.csv")
        # Buat kolom Datetime untuk mempermudah resampling grafik
        df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d-%m-%Y %H:%M:%S')
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['jarak', 'Intensitas_cahaya', 'isBuzzing', 'LEDisON', 'Date', 'Time', 'Datetime'])

df = load_data()

if df.empty:
    st.warning("Menunggu data... (File data.csv belum ada atau kosong)")
else:
    # --- BAGIAN ATAS: Grafik Statistik ---
    st.subheader("Grafik Statistik Rata-rata")
    
    interval_dict = {'Per Menit': 'min', 'Per Jam': 'h', 'Per Hari': 'D'}
    pilihan = st.selectbox("Pilih Interval Waktu:", list(interval_dict.keys()))
    freq = interval_dict[pilihan]

    df_resampled = df.set_index('Datetime').resample(freq)[['jarak', 'Intensitas_cahaya']].mean().reset_index()
    df_resampled = df_resampled.dropna()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Rata-rata Jarak**")
        st.line_chart(df_resampled.set_index('Datetime')['jarak'])
    
    with col2:
        st.markdown("**Rata-rata Intensitas Cahaya**")
        st.line_chart(df_resampled.set_index('Datetime')['Intensitas_cahaya'])

    st.divider()

    # --- BAGIAN TENGAH: Histori Aktifitas Terpisah ---
    st.subheader("Histori Aktifitas (Buzzer & LED)")
    
    col_buzz, col_led = st.columns(2)
    
    with col_buzz:
        st.markdown("**Histori Buzzer Menyala**")
        # Filter hanya saat buzzer bernilai 1
        df_buzzer = df[df['isBuzzing'] == 1].copy()
        
        if not df_buzzer.empty:
            df_buzzer = df_buzzer.sort_values(by='Datetime', ascending=False)
            # Menampilkan Date, Time, jarak, dan intensitas
            st.dataframe(
                df_buzzer[['Date', 'Time', 'jarak', 'Intensitas_cahaya']], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Belum ada histori Buzzer menyala.")

    with col_led:
        st.markdown("**Histori LED Menyala**")
        # Filter hanya saat LED bernilai 1
        df_led = df[df['LEDisON'] == 1].copy()
        
        if not df_led.empty:
            df_led = df_led.sort_values(by='Datetime', ascending=False)
            # Menampilkan Date, Time, jarak, dan intensitas
            st.dataframe(
                df_led[['Date', 'Time', 'jarak', 'Intensitas_cahaya']], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Belum ada histori LED menyala.")

    st.divider()

    # --- BAGIAN BAWAH: Histori Keseluruhan ---
    st.subheader("Tabel Histori Keseluruhan")
    df_history = df.sort_values(by='Datetime', ascending=False).drop(columns=['Datetime'])
    st.dataframe(df_history, use_container_width=True, hide_index=True)