import serial
import csv
import os
import time
from datetime import datetime

# Sesuaikan port dengan COM port ESP32 di devicemu (misal 'COM3' untuk Windows, '/dev/ttyUSB0' untuk Linux)
SERIAL_PORT = 'COM3' 
BAUD_RATE = 115200
CSV_FILE = 'data.csv'

# Setup header CSV jika file belum ada
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['jarak', 'Intensitas_cahaya', 'isBuzzing', 'LEDisON', 'Date', 'Time'])

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Terkoneksi. Mendengarkan data di {SERIAL_PORT}...")
except serial.SerialException as e:
    print(f"Gagal membuka port serial: {e}")
    exit()

while True:
    try:
        if ser.in_waiting > 0:
            # Baca line dari ESP32
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            data = line.split(',')
            
            # Pastikan data yang diterima lengkap 4 parameter
            if len(data) == 4:
                # Dapatkan Date dan Time saat ini
                now = datetime.now()
                current_date = now.strftime('%d-%m-%Y')
                current_time = now.strftime('%H:%M:%S')
                
                # Susun row
                row = [data[0], data[1], data[2], data[3], current_date, current_time]
                
                # Append ke CSV
                with open(CSV_FILE, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(row)
                
                print(f"[{current_time}] Data tersimpan: {row}")
            else:
                print(f"Format tidak valid atau incomplete payload: {line}")
                
        time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nReceiver dihentikan.")
        break
    except Exception as e:
        print(f"Error: {e}")