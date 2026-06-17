import paho.mqtt.client as mqtt
import json
import sqlite3
import os

MQTT_BROKER = "192.168.1.5"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/lab/sensor"
DB_FILE = "weather_data.db"

#  Initialize the Local SQLite Database 
print("Initializing local storage database...")
db_conn = sqlite3.connect(DB_FILE, check_same_thread=False)
db_cursor = db_conn.cursor()

# Create table structured to hold readings
db_cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temperature REAL,
        humidity REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
db_conn.commit()
print(f"Database ready. Saving data to: {os.path.abspath(DB_FILE)}")

# Define Data Processing Triggers
def on_connect(client, userdata, flags, rc, properties=None):
    """Triggered when the script logs into the MQTT network."""
    if rc == 0:
        print(f"Connected to MQTT Broker! Monitoring topic: '{MQTT_TOPIC}'...")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Connection failed with error code: {rc}")

def on_message(client, userdata, msg):
    """Triggered automatically every time Wokwi sends a payload."""
    try:
        payload_string = msg.payload.decode('utf-8')
        print(f"\nIncoming data packet caught: {payload_string}")
        
        data = json.loads(payload_string)
        
        temp = data.get("temp")
        hum = data.get("humidity")
        
        if temp is not None and hum is not None:
            db_cursor.execute(
                "INSERT INTO weather_readings (temperature, humidity) VALUES (?, ?)", 
                (temp, hum)
            )
            db_conn.commit()
            print(" Packet saved cleanly to local SQLite storage.")
        else:
            print(" Warning: Received JSON lacks 'temp' or 'humidity' keys.")
        
    except json.JSONDecodeError:
        print(" Malformed data packet rejected (Not valid JSON).")
    except Exception as error:
        print(f" Storage pipeline error: {error}")

# Run the Storage Worker Pipeline
storage_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
storage_client.on_connect = on_connect
storage_client.on_message = on_message

# Launch network connection loop
try:
    storage_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    storage_client.loop_forever()
except KeyboardInterrupt:
    print("\nStopping database logger pipeline. Saving states...")
    db_conn.close()
    print("Database connection closed successfully.")

