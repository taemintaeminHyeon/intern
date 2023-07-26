#include <WiFi.h>
#include <HTTPClient.h>
#include <PubSubClient.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

// Wi-Fi 정보
const char* ssid = "Jimbo";
const char* password = "jbrjbrjbr1";

// HTTP POST 요청 보낼 서버 정보
const char* serverUrl = "http://192.168.0.152:2250/api/sendRobotInfo";

// MQTT 브로커 정보
const char* mqtt_server = "192.168.0.152";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

// 시간 추적을 위한 변수
unsigned long previousHTTPMillis = 0;
const unsigned long httpInterval = 200; // 0.2초

// Task 핸들러 변수
TaskHandle_t httpTask;
TaskHandle_t mqttTask;

// 메시지 수신 콜백 함수
void callback(char* topic, byte* payload, unsigned int length) {
  // 수신한 메시지를 문자열로 변환
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  // 수신한 메시지 처리
  Serial.print("Received message [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);
}

// HTTP Task
void httpTaskFunction(void* parameter) {
  for (;;) {
    // 현재 시간을 가져옵니다.
    unsigned long currentMillis = millis();

    // HTTP POST 요청 보내기 - 0.2초마다 한 번씩 보냅니다.
    if (currentMillis - previousHTTPMillis >= httpInterval) {
      previousHTTPMillis = currentMillis;

      // HTTP 요청 보내는 코드
      String dataToSend = "robot1, robot1111111111111111111111111111111111";

      HTTPClient http;
      http.begin(serverUrl);
      http.addHeader("Content-Type", "text/plain");

      int httpResponseCode = http.POST(dataToSend);
      if (httpResponseCode > 0) {
        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);
        String response = http.getString();
        Serial.println("Response: " + response);
      } else {
        Serial.print("Error on sending request. HTTP Response code: ");
        Serial.println(httpResponseCode);
      }

      http.end();
    }

    vTaskDelay(100); // 0.1초 지연
  }
}

// MQTT Task
void mqttTaskFunction(void* parameter) {
  for (;;) {
    client.loop(); // MQTT 브로커로부터 메시지를 처리합니다.
    vTaskDelay(10); // 0.01초 지연
  }
}

void setup() {
  Serial.begin(115200);

  // Wi-Fi 연결
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);

  // MQTT 브로커에 연결
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  while (!client.connected()) {
    if (client.connect("robot1")) {
      Serial.println("Connected to MQTT Broker");
      // ESP32가 구독하는 토픽을 설정합니다.
      client.subscribe("robot1");
    } else {
      Serial.print("Failed to connect to MQTT Broker, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }

  // Task 생성
  xTaskCreate(httpTaskFunction, "HTTP Task", 2048, NULL, 1, &httpTask);
  xTaskCreate(mqttTaskFunction, "MQTT Task", 2048, NULL, 1, &mqttTask);
}

void loop() {
  
}