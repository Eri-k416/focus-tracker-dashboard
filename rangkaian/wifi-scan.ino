const int buzled = 19;
const int led = 18;
const int echoULS = 16;
const int trigULS = 17;
const int analogPRS = 34;

int penaltyTime = 0;
int maxPenaltyTime = 10;

// Tambahan variabel waktu pengganti delay
unsigned long lastLoopTime = 0;
unsigned long lastBuzzerTime = 0;
bool statusBuzzer = false;

void setup() {
  Serial.begin(115200);
  pinMode(buzled, OUTPUT);
  pinMode(led, OUTPUT);
  pinMode(echoULS, INPUT);
  pinMode(trigULS, OUTPUT);
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
      noTone(buzled); // Memastikan buzzer berhenti saat jarak kembali aman
      statusBuzzer = false;
    }
  }
}