/*
 * Basics
 */
#include <string.h>

/*
 * LED Matrix
 */
// To use ArduinoGraphics APIs, please include BEFORE Arduino_LED_Matrix
#include "ArduinoGraphics.h"
#include "Arduino_LED_Matrix.h"
ArduinoLEDMatrix matrix;

/*
 * Network
 */
#include "WiFiS3.h"
#include "WiFiSSLClient.h"
#include "IPAddress.h"
#include "network_secrets.h" 

/*
 * Temp/humidity sensor
 */
#include "DFRobot_AHT20.h"
DFRobot_AHT20 aht20;

/*
 * IR sensor
 */
#include <DFRobot_MLX90614.h>
DFRobot_MLX90614_I2C sensor_ir;   // instantiate an object to drive our sensor

/*
 * Variables
 */
uint8_t RETRY = 3;
uint8_t essai = 0;
uint8_t status;
char phrase[100];
char tmp[30];
bool aht20_dispo = false;
bool sensor_ir_dispo = false;

char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS; 
char server[] = "iotlog.ywo.fr";
WiFiSSLClient client;


void setup(){
  
  Serial.begin(115200);

  while(!Serial){
    //Wait for USB serial port to connect. Needed for native USB port only
  }
  Serial.println("Serial OK");
  
  /**
   * @fn begin
   * @brief Initialize AHT20 sensor
   * @return Init status value
   * @n      0    Init succeeded
   * @n      1    _pWire is NULL, please check if the constructor DFRobot_AHT20 has correctly uploaded a TwoWire class object reference
   * @n      2    Device not found, please check if the connection is correct
   * @n      3    If the sensor init fails, please check if there is any problem with the sensor, you can call the reset function and re-initialize after restoring the sensor
   */
  essai = 0;
  while((status = aht20.begin()) != 0 && essai < RETRY){
    Serial.print("AHT20 sensor initialization failed. error status : ");
    Serial.println(status);
    delay(1000);
    essai++;
  }
  if(status == 0) {
    Serial.println("Thermometre AHT20 OK");
    aht20_dispo = true;
  } else {
    Serial.println("Thermometre AHT20 FAIL");
    aht20_dispo = false;
  }

  essai = 0;
  while( NO_ERR != (status = sensor_ir.begin()) && essai < RETRY ){
    Serial.println("Communication with device failed, please check connection");
    Serial.print("Status = ");
    Serial.println(status);
    delay(1000);
    essai++;
  }
  if(status == NO_ERR) {
    Serial.println("Thermometre MLX90614 OK");
    sensor_ir_dispo = true;
  } else {
    Serial.println("Thermometre MLX90614 FAIL");
    sensor_ir_dispo = false;
  }
  
  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }
  
  String fv = WiFi.firmwareVersion();
  Serial.print("WiFi firmware is in version = ");
  Serial.println(fv);
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware");
  }

  status = WL_IDLE_STATUS;
  // attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network.
    status = WiFi.begin(ssid, pass);
    // wait 1 second for connection
    delay(1000);
  }

  printWifiStatus();

  /* Matrix initialization */
  matrix.begin();
  Serial.println("Matrix OK");
  
  matrix.beginDraw();
  matrix.stroke(0xFFFFFFFF);
  // add some static text
  // will only show first three letters
  const char text[] = "Gui";
  matrix.textFont(Font_4x6);
  matrix.beginText(0, 1, 0xFFFFFF);
  matrix.println(text);
  matrix.endText();
  matrix.endDraw();

  delay(500);

}


/* -------------------------------------------------------------------------- */
void printWifiStatus() {
/* -------------------------------------------------------------------------- */  
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print your gateway's IP address:
  Serial.print("Gateway Address: ");
  Serial.println(WiFi.gatewayIP());

  // print your DNS's IP address:
  Serial.print("DNS Address: ");
  Serial.println(WiFi.dnsIP());

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}

void sendData(char *key, char *value) {
  char get[100];
  Serial.println("Starting connection to server...");
  // if you get a connection, report back via serial:
  
  client.connect(server, 443);
  
  strcpy(get, "GET /post?");
  strcat(get, key);
  strcat(get, "=");
  strcat(get, value);
  strcat(get, " HTTP/1.1");
  client.println(get);
  client.println("Host: iotlog.ywo.fr");
  client.println("User-Agent: Arduino/4.0 (Arduino Uno R4 WiFi)");
  client.println("Connection: close");
  client.println("");

  Serial.println("Data sent.");
  client.stop();
}

void textScroll(char * text) {
  char tmp[105];
  strcpy(tmp, "   ");
  strcat(tmp, text);
  // Make it scroll!
  matrix.beginDraw();
  matrix.stroke(0xFFFFFFFF);
  matrix.textScrollSpeed(40);
  // add the text
  matrix.textFont(Font_5x7);
  matrix.beginText(0, 1, 0xFFFFFF);
  matrix.println(tmp);
  matrix.endText(SCROLL_LEFT);
  matrix.endDraw();
}

void loop(){

  Serial.println("########## LOOP ##########");

  if(aht20_dispo) {
    if(aht20.startMeasurementReady(/* crcEn = */true)){
      // Affichage de la temperature
      strcpy(phrase, "T = ");
      sprintf(tmp, "%5.2f", aht20.getTemperature_C());
      strcat(phrase, tmp);
      strcat(phrase, "°C");
      Serial.println(phrase);
      textScroll(phrase);
      sendData("aht20_t_grenier", tmp);
      // Affichage de l'humidité relative
      strcpy(phrase, "H = ");
      sprintf(tmp, "%5.2f", aht20.getHumidity_RH());
      strcat(phrase, tmp);
      strcat(phrase, "%");
      Serial.println(phrase);
      textScroll(phrase);
      sendData("aht20_h_grenier", tmp);
    } else {
      Serial.println("Erreur lors de la lecture du capteur de temperature.");
      textScroll("erreur");
    }
  } else {
    Serial.println("Capteur de temperature non detecte.");
  }

  if(sensor_ir_dispo) {
    /**
     * get ambient temperature, unit is Celsius
     * return value range： -40.01 °C ~ 85 °C
     */
    float ambientTemp = sensor_ir.getAmbientTempCelsius();
    Serial.print("Ambient celsius : "); Serial.print(ambientTemp); Serial.println(" °C");
    // Affichage de la temperature ambiante
    strcpy(phrase, "Ambiant = ");
    sprintf(tmp, "%5.2f", ambientTemp);
    strcat(phrase, tmp);
    strcat(phrase, "°C");
    Serial.println(phrase);
    textScroll(phrase);
    /**
     * get temperature of object 1, unit is Celsius
     * return value range： 
     * @n  -70.01 °C ~ 270 °C(MLX90614ESF-DCI)
     * @n  -70.01 °C ~ 380 °C(MLX90614ESF-DCC)
     */
    float objectTemp = sensor_ir.getObjectTempCelsius();
    Serial.print("Object celsius : ");  Serial.print(objectTemp);  Serial.println(" °C");
    // Affichage de la temperature de l'objet
    strcpy(phrase, "Objet = ");
    sprintf(tmp, "%5.2f", objectTemp);
    strcat(phrase, tmp);
    strcat(phrase, "°C");
    Serial.println(phrase);
    textScroll(phrase);
  } else {
    Serial.println("Capteur infrarouge non detecte.");
  }

  // wait 15 minutes
  delay(900000);
}
