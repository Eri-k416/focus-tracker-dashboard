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

    # Agregasi (Rata-rata) berdasarkan interval waktu yang dipilih
    df_resampled = df.set_index('Datetime').resample(freq)[['jarak', 'Intensitas_cahaya']].mean().reset_index()
    # Hapus row yang NaN (jika pada interval tersebut tidak ada data)
    df_resampled = df_resampled.dropna()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Rata-rata Jarak**")
        st.line_chart(df_resampled.set_index('Datetime')['jarak'])
    
    with col2:
        st.markdown("**Rata-rata Intensitas Cahaya**")
        st.line_chart(df_resampled.set_index('Datetime')['Intensitas_cahaya'])

    st.divider()

    # --- BAGIAN TENGAH: Tabel Aktif (Buzz/LED ON) ---
    st.subheader("Histori Aktifitas (Buzzer / LED Menyala)")
    # Filter data hanya saat buzzer atau LED bernilai 1
    df_active = df[(df['isBuzzing'] == 1) | (df['LEDisON'] == 1)].copy()
    
    if not df_active.empty:
        # Urutkan dari yang terbaru
        df_active = df_active.sort_values(by='Datetime', ascending=False)
        st.dataframe(
            df_active[['Date', 'Time', 'jarak', 'Intensitas_cahaya', 'isBuzzing', 'LEDisON']], 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("Belum ada histori Buzzer atau LED menyala.")

    st.divider()

    # --- BAGIAN BAWAH: Histori Keseluruhan ---
    st.subheader("Tabel Histori Keseluruhan")
    df_history = df.sort_values(by='Datetime', ascending=False).drop(columns=['Datetime'])
    st.dataframe(df_history, use_container_width=True, hide_index=True)