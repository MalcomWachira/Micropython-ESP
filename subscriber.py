import paho.mqtt.client as mqtt
import json
from datetime import datetime

# --- Configuration Settings ---
# If Mosquitto is running on the SAME PC, use "localhost". 
# If it's on a different machine or cloud, use its IP address (e.g., "192.168.1.50").
MOSQUITTO_BROKER = "192.168.1.5" 
MOSQUITTO_PORT = 1883
MQTT_TOPIC = "iot/lab/sensor"
CLIENT_ID = "PC_Python_Subscriber_Node"

# --- Callback Functions ---
def on_connect(client, userdata, flags, rc, properties=None):
    """Triggered automatically when the script connects to Mosquitto."""
    if rc == 0:
        print(f"Successfully connected to Mosquitto Broker at [{MOSQUITTO_BROKER}]")
        # Subscribe to the target topic
        client.subscribe(MQTT_TOPIC)
        print(f"Monitoring topic: '{MQTT_TOPIC}'...\n")
    else:
        print(f"Connection failed with error code: {rc}")


def on_message(client, userdata, msg):
    """Triggered automatically every time the ESP32 publishes data."""
    try:
        # 1. Decode the raw binary network stream into a UTF-8 string
        payload_string = msg.payload.decode('utf-8')
        
        # 2. Parse the string into a Python dictionary
        sensor_data = json.loads(payload_string)
        
        # 3. Extract the requested fields
        temperature = sensor_data.get("temp")
        humidity = sensor_data.get("humidity")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 4. Print clean structured output to the console
        print(f"[{timestamp}] New Telemetry Received:")
        print(f"  ├── Temperature : {temperature} °C")
        print(f"  └── Humidity    : {humidity} %")
        print("-" * 40)
        
    except json.JSONDecodeError:
        print(f"❌ Error: Received malformed non-JSON data: {msg.payload}")
    except Exception as e:
        print(f"❌ Error processing message: {e}")

# --- Main Script Execution ---
# Initialize the Paho MQTT Client
# Tell the library you are using the modern Callback API version 2
subscriber_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)


# Assign our callback functions
subscriber_client.on_connect = on_connect
subscriber_client.on_message = on_message

try:
    print("Connecting to Mosquitto broker...")
    subscriber_client.connect(MOSQUITTO_BROKER, MOSQUITTO_PORT, 60)
    
    # Start a blocking loop that handles network traffic and auto-reconnects
    subscriber_client.loop_forever()
    
except KeyboardInterrupt:
    print("\nDisconnecting from broker. Exiting gracefully...")
    subscriber_client.disconnect()

