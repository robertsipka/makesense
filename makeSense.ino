  
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <arduinoFFT.h>
#include <MQ2.h>
#include "Adafruit_SHT31.h"
#include "HX711.h"
#include <BH1750FVI.h>
#include <string.h>
#include <SoftwareSerial.h>

SoftwareSerial bc66(A8, A9); // RX, TX

/*
 * Digital pin for read the box state (closed or not)
 * C (PIN 1)  ---- D7-----|10kOhm|--- 5V
 * NC (PIN 2) ---- GND
 */
#define BUTTON_PIN 7

/* 
 *  BMP specific pins
 *
 * VCC ----- 3.3V
 * GND ----- GND
 * SCL ----- D13
 * SDA ----- D11
 * CSB ----- D10
 * SDO ----- D12
 */
#define BMP_SCK 13
#define BMP_MISO 12
#define BMP_MOSI 11 
#define BMP_CS 10

/* 
 * MICROPHONE specific pins
 * VCC ----- 5V
 * GND ----- GND
 * A0  ----- A0
 */
#define MICROPHONE_CHANNEL A0
#define SAMPLES 256
#define FREQUENCY 2000
#define SCL_INDEX 0x00
#define SCL_TIME 0x01
#define SCL_FREQUENCY 0x02
#define SCL_PLOT 0x03

/*
 * GAS sensor specific pins
 * VCC ----- 5V
 * GND ----- GND
 * A0  ----- A1
 */
#define MQ2_CHANNEL A1

/* 
 * SHT31D Temp and humidity specific pins
 * VSS ----- GND
 * SCL ----- A5 v. SCL
 * SDA ----- A4 v. SDA
 * VDD ----- 3.3V
 */
#define SHT31_ADDR 0x44

/*
 * Rain sensor specific pins
 */
#define RAIN_CHANNEL A2

/*
* Scale specific pins
* VCC ----- 5VV
* GND ----- GND
* SCL ----- D2   D4
* SDA ----- D3   D5
*/
#define LOADCELL_DOUT_PIN 4
#define LOADCELL_SCK_PIN 5
#define CALIBRATION_TARE 33715
#define CALIBRATION_CONST 445.3

/* 
* BH1750FVI Light sensor
* GND ----- GND
* SCL ----- A5 v. SCL
* SDA ----- A4 v. SDA
* VDD ----- 3.3V
*/
//#define BH1750FVI_ADDR 0x23 // begin(void) we don't have to specify, it is automatic

// bmp sensor
Adafruit_BMP280 bmp(BMP_CS, BMP_MOSI, BMP_MISO,  BMP_SCK);
// gas sensor
MQ2 mq2(MQ2_CHANNEL);
// humidity sensor
Adafruit_SHT31 sht31 = Adafruit_SHT31();
// scale sensor
HX711 scale;
// Light sensor
BH1750FVI LightSensor(BH1750FVI::k_DevModeContLowRes);

void setup() {
  // Serial.begin(115200);
  //Serial.begin(9600);
  delay(1000);
  bc66.begin(9600);
  delay(1000);

  Serial.println("Kibu - SOS Electronic NBIoT Test");
  delay(1000);
  bc66.println("AT+SM=LOCK");
  if ( bc66.available() ) Serial.write( bc66.read() );
  delay(1000);
  bc66.println("AT+QSCLK=0");
  if ( bc66.available() ) Serial.write( bc66.read() );
  delay(1000);
  bc66.println("AT+QGACT=1,1,\"u.iot.mt.gr.hu\"");
  if ( bc66.available() ) Serial.write( bc66.read() );
  delay(5000);
  bc66.println("AT+QSOC=1,2,1");
  if ( bc66.available() ) Serial.write( bc66.read() );
  delay(1000);
  // bc66.println("AT+QSOCON=0,41234,\"188.166.124.211\"");
  bc66.println("AT+QSOCON=0,1234,\"18.194.96.218\"");
  if ( bc66.available() ) Serial.write( bc66.read() );
  delay(1000);
  Serial.println("Connection established");

  // initialize the box state button
  pinMode(BUTTON_PIN, INPUT); 

  // check the bmp sensor
  Serial.println(F("BMP280 test"));
  if (!bmp.begin()) {
    Serial.println(F("Could not find a valid BMP280 sensor, check wiring!"));
    //loop runs for eternity until switched off
    while (1) delay(1);
  }

  // gas sensor
  Serial.println(F("MQ-2 test"));
  mq2.begin();

  // check the SHT31D sensor
  Serial.println(F("SHT31D test"));  
  if (!sht31.begin(SHT31_ADDR)) {
    Serial.println("Could not find a valid SHT31D sensor, check wiring!");
    //loop runs for eternity until switched off
    while (1) delay(1);
  }

  //  check the HX711 scale
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  delay (200);
  Serial.println(F("Weight scale HX711 test"));  
  if (!scale.is_ready()) {
    Serial.println("Could not find a valid Weight scale HX711 sensor, check wiring!");
    //loop runs for eternity until switched off
    while (1) delay(1);
  }

  // Light sensor
  Serial.println(F("BH1750FVI light sensor test"));
  LightSensor.begin();  

}

int msg_length = 0;

void loop() {
  char msg[2048] = "";
  msg_length = 0;
  float is_closed = digitalRead(BUTTON_PIN);

  float bmp_temp = bmp.readTemperature();
  float bmp_pressure = bmp.readPressure();
  float bmp_altitude = bmp.readAltitude(1013.25);

  arduinoFFT FFT = arduinoFFT(); /* Create FFT object */
  double vReal[SAMPLES];
  double vImag[SAMPLES];

  // sampling of the microphone
  unsigned long microseconds = micros();
  unsigned int sampling_period_us = round(1000000*(1.0/FREQUENCY));

  for (int i = 0; i < SAMPLES; i++) {
    while (micros() - microseconds < sampling_period_us) {
      // wait for the right time to take the sample
    }
    
    // update as per the period
    microseconds += sampling_period_us;
    vReal[i] = analogRead(MICROPHONE_CHANNEL);
    vImag[i] = 0;
  }


  FFT.Windowing(vReal, SAMPLES, FFT_WIN_TYP_HAMMING, FFT_FORWARD);  /* Weigh data */
  FFT.Compute(vReal, vImag, SAMPLES, FFT_FORWARD); /* Compute FFT */
  FFT.ComplexToMagnitude(vReal, vImag, SAMPLES); /* Compute magnitudes */
  double major_peak = FFT.MajorPeak(vReal, SAMPLES, FREQUENCY);

  /*
   * read the values from the sensor, it returns an array which contains 3 values.
   * 0 = LPG in ppm
   * 1 = CO in ppm
   * 2 = SMOKE in ppm
   */
  float* gas_values = mq2.read(false); //set it true if you want to print the values in the Serial
 
  /*
   * read the values from the SHT31 sensor
   */
  float sht31_temp = sht31.readTemperature();
  float sht31_humidity = sht31.readHumidity();
  
  /*
   * read the values from the RAIN sensor
   */
  float rain_sensor_value = analogRead(RAIN_CHANNEL);
  /*
   * read the average values from the scale sensor and calculate the weigth in gramms
   */
  float weight = (scale.read_average(20) - CALIBRATION_TARE) / CALIBRATION_CONST;
  
  /*
   * read the values from the Light sensor
   */
  float lux = LightSensor.GetLightIntensity();

  // sensor data
  memcpy(msg, "AT+QSOSEND=0,564,", 17);
  msg_length = 17;
  append_message(is_closed, msg);
  append_message(gas_values[0], msg);
  append_message(gas_values[1], msg);
  append_message(gas_values[2], msg);
  append_message(bmp_temp, msg);
  append_message(bmp_pressure, msg);
  append_message(bmp_altitude, msg);
  append_message(sht31_temp, msg);
  append_message(sht31_humidity, msg);
  append_message(rain_sensor_value, msg);
  append_message(weight, msg);
  append_message(lux, msg);
  append_message((float)major_peak, msg);

  for (uint16_t i = 0; i < SAMPLES >> 1; i++)
  {
    append_message((float)vReal[i],msg);
  }

  msg[msg_length] = '\n';
  bc66.println(msg);

  Serial.println(msg);

  //set the repetition of the data in ms
  delay(10000);
  
}

typedef union
{
 float number;
 uint8_t bytes[4];
} FLOATUNION_t;

void append_message(float f, char msg[]) {
  FLOATUNION_t myFloat;
  myFloat.number = f;
  array_to_string(myFloat.bytes, 4, msg);
}

void array_to_string(byte array[], unsigned int len, char msg[])
{
    for (unsigned int i = 0; i < len; i++)
    {
        byte nib1 = (array[i] >> 4) & 0x0F;
        byte nib2 = (array[i] >> 0) & 0x0F;
        msg[msg_length + i*2+0] = nib1  < 0xA ? '0' + nib1  : 'A' + nib1  - 0xA;
        msg[msg_length + i*2+1] = nib2  < 0xA ? '0' + nib2  : 'A' + nib2  - 0xA;
    }
    msg_length += 8;
}