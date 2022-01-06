#include <MQTT.h>
#include "esp_camera.h"
#include <WiFi.h>


#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

#define LED_ON 33

MQTTClient client;
WiFiClient net;

// wifi information
const char* ssid = "P0w3r Rang3r";
const char* password = "TN150871";

// mqtt information
const char* broker = "broker.emqx.io";
const char* topic = "/Team10/car_controller";
const char* client_id = "ESP32";

void MQTT_CONNECT() {
  Serial.print("\nconnecting...");
  
  while (!client.connect(client_id)) {
    Serial.print(".");
    delay(1000);
  }
  
  Serial.println("\nconnected!");
  client.subscribe(topic);
}

void messageReceived(String &topic, String &payload) {
  if (payload == "F") {
    Serial.write('F');
    Serial.println(payload);
  }
  else if (payload == "B") {
    Serial.write('B');
    Serial.println(payload);
  }
  else if (payload == "L") {
    Serial.write('L');
    Serial.println(payload);
  }
  else if (payload == "R") {
    Serial.write('R');
    Serial.println(payload);
  }
  else if (payload == "G") {
    Serial.write('G');
    Serial.println(payload);
  }
  else if (payload == "I") {
    Serial.write('I');
    Serial.println(payload);
  }
  else if (payload == "H") {
    Serial.write('H');
    Serial.println(payload);
  }
  else if (payload == "J") {
    Serial.write('J');
    Serial.println(payload);
  }
  else if (payload == "S") {
    Serial.write('S');
    Serial.println(payload);
  }
}

void startCameraServer();

void setup() {
  Serial.begin(9600);
  Serial.setDebugOutput(true);
  Serial.println();

  pinMode(LED_ON, OUTPUT);
  digitalWrite(LED_ON, HIGH); 

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
  if(psramFound()){
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    while (1){
      digitalWrite(33, HIGH); 
      delay(500);
      digitalWrite(33, LOW);
      delay(500);
    }
  }

  sensor_t * s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1); // flip it back
    s->set_brightness(s, 1); // up the brightness just a bit
    s->set_saturation(s, -2); // lower the saturation
  }
  // drop down frame size for higher initial frame rate
  s->set_framesize(s, FRAMESIZE_QVGA);

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");

  client.begin(broker, net);
  client.onMessage(messageReceived);
  MQTT_CONNECT();
  
  digitalWrite(LED_ON, LOW); 
  Serial.write(';');
} 

void loop() {
  client.loop();
  delay(10); // <- fixes some issues with WiFi stability
  if (!client.connected()) {
    MQTT_CONNECT();
  }
}
