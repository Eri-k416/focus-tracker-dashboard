import paho.mqtt.client as mqtt
import csv
import os
from datetime import datetime

# --- Konfigurasi MQTT HiveMQ ---
# Gunakan broker publik HiveMQ atau sesuaikan dengan URL HiveMQ Cloud Anda
MQTT_BROKER = "broker.hivemq.com"  
MQTT_PORT = 1883                   # Port standar non-TLS (Gunakan 8883 jika pakai TLS/SSL Cloud)
MQTT_TOPIC = "esp32/sensor/data"   # Sesuaikan dengan topic yang dipublish oleh ESP32 Anda
CSV_FILE = 'data.csv'

# Setup header CSV jika file belum ada
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['jarak', 'Intensitas_cahaya', 'isBuzzing', 'LEDisON', 'Date', 'Time'])

# Callback saat terhubung ke broker
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Berhasil terhubung ke MQTT Broker: {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
        print(f"Mendengarkan data pada topik: {MQTT_TOPIC}")
    else:
        print(f"Gagal koneksi ke broker, kode error: {rc}")

# Callback saat pesan MQTT diterima
def on_message(client, userdata, msg):
    try:
        # Ambil payload pesan (format string koma: jarak,Intensitas_cahaya,isBuzzing,LEDisON)
        payload = msg.payload.decode('utf-8').strip()
        data = payload.split(',')
        
        # Pastikan data lengkap 4 parameter
        if len(data) == 4:
            now = datetime.now()
            current_date = now.strftime('%d-%m-%Y')
            current_time = now.strftime('%H:%M:%S')
            
            # Susun baris data untuk CSV
            row = [data[0], data[1], data[2], data[3], current_date, current_time]
            
            # Simpan ke CSV
            with open(CSV_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)
            
            print(f"[{current_time}] Data MQTT tersimpan: {row}")
        else:
            print(f"Format payload tidak valid (harus 4 parameter): {payload}")
            
    except Exception as e:
        print(f"Error memproses pesan: {e}")

def main():
    # Inisialisasi MQTT Client (Mendukung paho-mqtt v2 & v1)
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    # --- KONFIGURASI TAMBAHAN JIKA MENGGUNAKAN HIVEMQ CLOUD (BERBAYAR/CLUSTER) ---
    # Jika HiveMQ Cloud Anda memerlukan autentikasi username & password, uncomment baris di bawah:
    # client.username_pw_set("USERNAME_ANDA", "PASSWORD_ANDA")
    # client.tls_set()  # Wajib diaktifkan untuk HiveMQ Cloud (biasanya port 8883)

    print(f"Menghubungkan ke {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Memulai loop background untuk menerima pesan secara terus-menerus
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nReceiver MQTT dihentikan.")
        client.disconnect()

if __name__ == "__main__":
    main()