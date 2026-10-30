#include <WiFi.h>
#include <PubSubClient.h>

// config wifi dan mqtt
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic = "sic8/katasakirayoaja/studycase/studytracker"; 

WiFiClient espClient;
PubSubClient client(espClient);

const int buzled = 19;
const int led = 18;
const int echoULS = 16;
const int trigULS = 17;
const int analogPRS = 34;

int penaltyTime = 0;
int maxPenaltyTime = 10;

unsigned long lastLoopTime = 0;
unsigned long lastBuzzerTime = 0;
bool statusBuzzer = false;

// Fungsi untuk menyambungkan WiFi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Menghubungkan ke WiFi: ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi Terhubung!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

// Fungsi memastikan koneksi ke MQTT Broker tetap terjaga
void reconnect() {
  while (!client.connected()) {
    Serial.print("Menghubungkan ke MQTT Broker...");
    String clientId = "ESP32Client-" + String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("Terhubung!");
    } else {
      Serial.print("Gagal, rc=");
      Serial.print(client.state());
      Serial.println(" coba lagi dalam 2 detik");
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(buzled, OUTPUT);
  pinMode(led, OUTPUT);
  pinMode(echoULS, INPUT);
  pinMode(trigULS, OUTPUT);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void peringatan(int pin) {
  // Pengganti delay(1000) agar nyala-mati tiap 1 detik tanpa memblokir program
  if (millis() - lastBuzzerTime >= 1000) {
    lastBuzzerTime = millis();
    statusBuzzer = !statusBuzzer;

    if (statusBuzzer) {
      tone(pin, 1000);
    } else {
      noTone(pin);
    }
  }
}

void trigUltraSonik(int pin) {
  digitalWrite(pin, LOW);
  delayMicroseconds(2);
  digitalWrite(pin, HIGH);
  delayMicroseconds(10);
  digitalWrite(pin, LOW);
}

int echoUltraSonik(int pin) {
  int duration = pulseIn(pin, HIGH);
  int distance = duration * 0.034 / 2;

  return distance;
}

int deteksiCahaya() {
  int rawValue = analogRead(analogPRS);
  int persentaseCahaya = map(rawValue, 32, 4063, 100, 0);

  int nilaiCahaya = constrain(persentaseCahaya, 0, 100);

  return nilaiCahaya;
}

void nyalaLampu(int nilaiCahaya) {
  analogWrite(led, nilaiCahaya);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Pengganti delay(500) menggunakan millis()
  if (millis() - lastLoopTime >= 500) {
    lastLoopTime = millis();

    int nilaiCahaya = deteksiCahaya();

    if (nilaiCahaya < 50) {
      Serial.print("Nilai : ");
      Serial.print(nilaiCahaya);
      Serial.println(" Kondisi  Gelap");
    } else {
      Serial.print("Nilai : ");
      Serial.print(nilaiCahaya);
      Serial.println(" Kondisi Terang");
    }

    int terangLampu;
    if (nilaiCahaya < 50) {
      terangLampu = (100 - nilaiCahaya) * 2;
    } else {
      terangLampu = 0;
    }

    nyalaLampu(terangLampu);

    trigUltraSonik(trigULS);
    int jarak = echoUltraSonik(echoULS);

    if (jarak > 70) {
      if (penaltyTime > maxPenaltyTime) {
        peringatan(buzled);
      } else {
        penaltyTime++;
      }
    } else {
      penaltyTime = 0;
      noTone(buzled); 
      statusBuzzer = false;
    }

// bungkus data manual ke format json menggunakan snprintf
    char jsonBuffer[256];
    snprintf(jsonBuffer, sizeof(jsonBuffer),
             "{\"cahaya\":%d,\"kondisi_cahaya\":\"%s\",\"pwm_lampu\":%d,\"jarak\":%d,\"penalty_time\":%d,\"peringatan_aktif\":%s}",
             nilaiCahaya,
             (nilaiCahaya < 50) ? "Gelap" : "Terang",
             terangLampu,
             jarak,
             penaltyTime,
             (jarak > 70 && penaltyTime > maxPenaltyTime) ? "true" : "false");

    client.publish(mqtt_topic, jsonBuffer);

    Serial.print("Kirim MQTT JSON: ");
    Serial.println(jsonBuffer);
  }
}