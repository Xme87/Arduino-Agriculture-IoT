#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266WebServer.h>
#include <FS.h>
#include <PubSubClient.h>
#include <DHT.h>

#define DHTPIN D1
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);
 
// 设置wifi接入信息(请根据您的WiFi信息进行修改)
const char* ssid = "aterm-c00a9d-g";
const char* password = "8d521cf161df5";
const char* mqttServer = "192.168.10.113";
const int mqttPort = 7788;
 
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
 

const char* mqttUserName = "admin";         // 服务端连接用户名(需要修改)
const char* mqttPassword = "mosquitto";          // 服务端连接密码(需要修改)
const char* clientId = "arduino_1";          // 客户端id (需要修改)
const char* subTopic = "IoT for soil";        // 订阅主题(需要修改)
const char* pubTopic1 = "Soil Humidity";
const char* pubTopic2 = "Air Humidity";
const char* pubTopic3 = "Air Temperature";        // 发布主题(需要修改)
const char* willTopic = "about to offline";   // 遗嘱主题名称  这是指，离线前最后一句话
// ****************************************************
 
//遗嘱相关信息
const char* willMsg = "esp8266 offline";        // 遗嘱主题信息
const int willQos = 0;                          // 遗嘱QoS
const int willRetain = false;                   // 遗嘱保留
 
const int subQoS = 1;           
const bool cleanSession = false; 
 
bool SensorStatus = LOW;

const long interval = 6000;  // 发送间隔，单位：毫秒（这里设置为一分钟）

unsigned long previousMillis = 0;
 
// 连接MQTT服务器并订阅信息
void connectMQTTserver(){
  // 根据ESP8266的MAC地址生成客户端ID（避免与其它ESP8266的客户端ID重名）
  
 
  /* 连接MQTT服务器
  boolean connect(const char* id, const char* user, 
                  const char* pass, const char* willTopic, 
                  uint8_t willQos, boolean willRetain, 
                  const char* willMessage, boolean cleanSession); 
  若让设备在离线时仍然能够让qos1工作，则connect时的cleanSession需要设置为false                
                  */
  if (mqttClient.connect(clientId, mqttUserName, 
                         mqttPassword
                         //, willTopic, 
                         //willQos, willRetain, willMsg, cleanSession
                         )) { 
    Serial.print("MQTT Server Connected. ClientId: ");
    Serial.println(clientId);
    Serial.print("MQTT Server: ");
    Serial.println(mqttServer);    
    
    subscribeTopic(); // 订阅指定主题
  } else {
    Serial.print("MQTT Server Connect Failed. Client State:");
    Serial.println(mqttClient.state());
    delay(5000);
  }   
}
 
// 收到信息后的回调函数
void receiveCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message Received [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println("");
  Serial.print("Message Length(Bytes) ");
  Serial.println(length);
 
  if ((char)payload[0] == '1') {     // 如果收到的信息以“1”为开始
    SensorStatus = HIGH;
    digitalWrite(A0, SensorStatus);  // 则开启传感器。
  } 
  if ((char)payload[0] == '2') {     // 如果收到的信息以“2”为开始
    SensorStatus = LOW;                           
    digitalWrite(A0, SensorStatus); // 则关闭传感器。
  }
 
  pubMQTTmsg();
}
 
// 订阅指定主题
void subscribeTopic(){
 
  
 
  if(mqttClient.subscribe(subTopic, subQoS)){
    Serial.print("Subscribed Topic: ");
    Serial.println(subTopic);
  } else {
    Serial.print("Subscribe Fail...");
  }  
}
 
// 发布信息
void pubMQTTmsg(){
  char* pubMessage1;
  char* pubMessage2;
  char* pubMessage3;

  int a = analogRead(0);
  char itc1[10];
  sprintf(itc1, "%d", a);
  pubMessage1 = itc1;

  float b = dht.readHumidity();
  char itc2[10];
  sprintf(itc2, "%f", b);
  pubMessage2 = itc2;

  float c = dht.readTemperature();
  char itc3[10];
  sprintf(itc3, "%f", c);
  pubMessage3 = itc3;
  
  /*if (SensorStatus == HIGH){
    int a = analogRead(0);
    char itc[10];
    sprintf(itc, "%d", a);
    pubMessage1 = itc;
  }*/

  // 实现ESP8266向主题发布信息
  if(mqttClient.publish(pubTopic1, pubMessage1)){
    Serial.println("Publish Topic:");Serial.println(pubTopic1);
    Serial.println("Publish message:");Serial.print(pubMessage1);    
  } else {
    Serial.println("Soil Humidity Publish Failed."); 
  }
    if(mqttClient.publish(pubTopic2, pubMessage2)){
    Serial.println("Publish Topic:");Serial.println(pubTopic2);
    Serial.println("Publish message:");Serial.print(pubMessage2);    
  } else {
    Serial.println("Air Humidity Publish Failed."); 
  }
    if(mqttClient.publish(pubTopic3, pubMessage3)){
    Serial.println("Publish Topic:");Serial.println(pubTopic3);
    Serial.println("Publish message:");Serial.print(pubMessage3);    
  } else {
    Serial.println("Air Temperature Publish Failed."); 
  }
}
 
// ESP8266连接wifi
void connectWifi(){
 
  WiFi.begin(ssid, password);
 
  //等待WiFi连接,成功连接后输出成功信息
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi Connected!");  
  Serial.println(""); 
}

void setup() {
  pinMode(A0, OUTPUT);          
  digitalWrite(A0, SensorStatus);
  dht.begin();  
  Serial.begin(57600);                   
  
  //设置ESP8266工作模式为无线终端模式
  WiFi.mode(WIFI_STA);
  
  // 连接WiFi
  connectWifi();
  
  // 设置MQTT服务器和端口号
  mqttClient.setServer(mqttServer, mqttPort);
  mqttClient.setCallback(receiveCallback);
 
  // 连接MQTT服务器
  connectMQTTserver();
}
 
void loop() {
  // 如果开发板未能成功连接服务器，则尝试连接服务器
  if (!mqttClient.connected()) {
    connectMQTTserver();
  }
 
   // 处理信息以及心跳
   mqttClient.loop();
    
  Serial.print("Soil Humidity:");
  Serial.println(analogRead(0));
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  Serial.print("Air Humidity: ");
  Serial.println(h);
  Serial.print("Air Temperature: ");
  Serial.print(t);
  Serial.println(" ℃ ");
  delay(500);  

  unsigned long currentMillis = millis();

  // 判断是否到达发送间隔
  if (currentMillis - previousMillis >= interval) {
    // 保存最后一次发送的时间
    previousMillis = currentMillis;

    // 发送 MQTT 消息
    pubMQTTmsg();
  }
}