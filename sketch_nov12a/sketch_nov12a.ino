#include <Wire.h> // Para a comunicação I2C
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// --- PINAGEM ---
// Multiplexador (Mux)
const int S0 = 1; // Pino de controle de endereço 0
const int S1 = 2; // Pino de controle de endereço 1
const int S2 = 3; // Pino de controle de endereço 2
const int MUX1_Z = 4; // Pino ADC para o Mux #1 (Pot 1 a 5)
const int MUX2_Z = 5; // Pino ADC para o Mux #2 (Pot 6 a 10)

// I2C para MPU-6050 (Remapeado)
// MPU #1 (AD0->GND) = 0x68 | MPU #2 (AD0->3.3V) = 0x69
const int SDA_PIN = 8; // Dados I2C
const int SCL_PIN = 9; // Clock I2C

// --- OBJETOS ---
Adafruit_MPU6050 mpu1; // MPU para o endereço 0x68
Adafruit_MPU6050 mpu2; // MPU para o endereço 0x69

// --- FUNÇÃO AUXILIAR ---
void selectMuxChannel(int channel) {
  // O Mux usa lógica binária para selecionar o canal (0 a 7)
  // O Mux só precisa de 3 bits: S0 (LSB), S1, S2 (MSB)
  digitalWrite(S0, bitRead(channel, 0));
  digitalWrite(S1, bitRead(channel, 1));
  digitalWrite(S2, bitRead(channel, 2));
  delayMicroseconds(5); // Pequeno atraso para o Mux estabilizar
}

void setup() {
  Serial.begin(115200);

  // Configura os pinos de controle do Mux como SAÍDA DIGITAL
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);

  // --- 1. TESTE I2C (MPU-6050) ---
  Wire.begin(SDA_PIN, SCL_PIN); // Inicializa I2C nos pinos remapeados (GPIO 8 e 9)

  Serial.println("--- Teste MPU-6050 (I2C) ---");
  
  // MPU #1 (Endereço 0x68)
  if (!mpu1.begin(0x68, &Wire)) {
    Serial.println("ERRO: MPU-6050 #1 (0x68) nao encontrado! Verifique o AD0 no GND.");
  } else {
    Serial.println("OK: MPU-6050 #1 (Pulso) inicializado.");
  }

  // MPU #2 (Endereço 0x69)
  if (!mpu2.begin(0x69, &Wire)) {
    Serial.println("ERRO: MPU-6050 #2 (0x69) nao encontrado! Verifique o AD0 no 3.3V.");
  } else {
    Serial.println("OK: MPU-6050 #2 (Antebraco) inicializado.");
  }
}

void loop() {
  // --- 2. TESTE ADC (POTENCIÔMETROS) ---
  //Serial.println("\n--- Leitura Potenciometros (ADC) ---");

  // Arrays para armazenar e exibir os dados dos potenciometros
  int pot_values[10]; 

  for (int i = 0; i < 5; i++) {
    // 1. Seleciona o canal 'i' nos dois Mux (Y0 a Y4)
    selectMuxChannel(i);

    // 2. Le o Potenciometro 'i' do Mux #1 (Pot 1 a 5)
    pot_values[i] = analogRead(MUX1_Z); 
    
    // 3. Le o Potenciometro 'i+5' do Mux #2 (Pot 6 a 10)
    pot_values[i + 5] = analogRead(MUX2_Z);
  }

  // Imprime os valores dos 10 Potenciometros
  for (int i = 0; i < 10; i++) {
    //Serial.print("Pot ");
    //Serial.print(i + 1);
    //Serial.print(": ");
    Serial.print(pot_values[i]);
    Serial.print(", ");
  }

  
  // --- 3. LEITURA MPU-6050 ---
  sensors_event_t a1, g1, temp1; // Eventos do MPU #1
  sensors_event_t a2, g2, temp2; // Eventos do MPU #2

  // Leitura MPU #1 (0x68)
  if (mpu1.getEvent(&a1, &g1, &temp1)) {
    //Serial.print("MPU #1 (0x68) Accel X: ");
    Serial.print(a1.acceleration.x);
    Serial.print(", ");
    Serial.print(g1.gyro.z);
    Serial.print(", ");
  } else {
    Serial.println("Erro ao ler MPU #1!");
  }

  // Leitura MPU #2 (0x69)
  if (mpu2.getEvent(&a2, &g2, &temp2)) {
    //Serial.print("MPU #2 (0x69) Accel X: ");
    Serial.print(a2.acceleration.x);
    Serial.print(", ");
    Serial.print(g2.gyro.z);
    Serial.println("");
  } else {
    Serial.println("Erro ao ler MPU #2!");
  }

  delay(200); // Aguarda 200ms antes da proxima leitura
}