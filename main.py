import network
import time
from machine import Pin
import dht
import ujson
from umqtt.simple import MQTTClient

# MQTT Server Parameters
MQTT_CLIENT_ID = "micropython dht22 lab"
MQTT_BROKER= "192.168.1.50"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "iot/lab/sensor"

sensor = dht.DHT22(Pin(15))

# connecting to wifi
print("Connecting to WiFi(Wokwi Virtual Wifi)", end="")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('iPhone', 'aa')
while not wlan.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Connected!")

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()

print("Connected!")

prev_weather = ""
while True:
  print("Measuring weather conditions... ", end="")
  sensor.measure() 
  message = ujson.dumps({
    "temp": sensor.temperature(),
    "humidity": sensor.humidity(),
  })
  if message != prev_weather:
    print("Updated!")
    print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC, message))
    client.publish(MQTT_TOPIC, message)
    prev_weather = message
  else:
    print("No change")
  time.sleep(1)
