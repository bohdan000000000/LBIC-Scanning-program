#include <Arduino.h>

const uint8_t  LASER_PIN  = 9;     // ШІМ-вихід на лазер 650 нм
const uint8_t  ADC_PIN    = A0;    // Вхід від TIA (LM358, Rf = 1 МОм)
const uint8_t  N_OVER     = 64;    // Кількість відліків для oversampling
const uint16_t SETTLE_US  = 5000;  // Час стабілізації після перемикання, мкс

enum State { IDLE, DARK, LIGHT, SEND };
State state = IDLE;

uint32_t oversample() {
    uint32_t sum = 0;
    for (uint8_t k = 0; k < N_OVER; k++) {
        sum += analogRead(ADC_PIN);
        delayMicroseconds(200);
    }
    return sum >> 3;
}

void setup() {
    Serial.begin(115200);
    pinMode(LASER_PIN, OUTPUT);
    digitalWrite(LASER_PIN, LOW);
    analogReference(DEFAULT);  

void loop() {
    static uint32_t v_dark = 0, v_light = 0;

    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();

        if (cmd == "MEASURE") {

            // Темнове вимірювання
            state = DARK;
            digitalWrite(LASER_PIN, LOW);
            delayMicroseconds(SETTLE_US);
            v_dark = oversample();

            // Світлове вимірювання
            state = LIGHT;
            digitalWrite(LASER_PIN, HIGH);
            delayMicroseconds(SETTLE_US);
            v_light = oversample();
            digitalWrite(LASER_PIN, LOW);

            // Передача диференційного сигналу на ПК
            state = SEND;
            int32_t v_photo = (int32_t)v_light - (int32_t)v_dark;
            Serial.print("DATA:");
            Serial.println(v_photo);

            state = IDLE;
        }
    }
}
