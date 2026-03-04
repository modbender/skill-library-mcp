import paho.mqtt.client as mqtt
import time
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(asctime)s [%(levelname)s] %(message)s")

BROKER   = os.getenv('MQTT_BROKER', 'localhost')
PORT     = int(os.getenv('MQTT_PORT', '1883'))
TOPIC    = os.getenv('MQTT_TOPIC', '#')
USER     = os.getenv('MQTT_USERNAME', '')
PASSWORD = os.getenv('MQTT_PASSWORD', '')
KEEPALIVE = 60 # This is the keep-alive timer for an *established* connection

# Callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.warning("Connected successfully.")
        client.subscribe("#") # Subscribe to all topics on successful connect
    else:
        logging.error(f"Connection failed, result code {rc}. Will retry...")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logging.warning("Unexpected disconnection. Automatic reconnection will be attempted by loop_start().")

def on_message(client, userdata, msg):
    logging.info(f"Received message: {msg.topic} - {msg.payload.decode()}")

# Main execution
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.username_pw_set(USER, PASSWORD)

try:
    # Connect to the broker (this is a non-blocking call in a threaded loop)
    client.connect(BROKER, PORT, KEEPALIVE)
    
    # Start the background network loop thread, which handles connection/reconnection
    client.loop_start() 
    
    logging.info("Client loop started. Running for 60 seconds...")

    # Keep the main program running for a specific duration
    start_time = time.time()
    while time.time() - start_time < 60:
        time.sleep(1) # Sleep briefly to avoid a busy loop

finally:
    # Ensure a graceful shutdown
    logging.info("60 seconds elapsed. Disconnecting...")
    client.disconnect()
    client.loop_stop() # Stop the background thread
    logging.info("Client disconnected and loop stopped.")

