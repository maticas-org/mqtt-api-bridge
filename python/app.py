import json
import paho.mqtt
from paho.mqtt import client as mqtt
import requests
import paho

from os import getenv
from dotenv import load_dotenv

load_dotenv()
API_KEY = getenv('API_KEY')
API_ENDPOINT = getenv('API_ENDPOINT')
MQTT_BROKER = getenv('MQTT_BROKER')
MQTT_PORT = int(getenv('MQTT_PORT'))
MQTT_USERNAME = getenv('MQTT_USERNAME')
MQTT_PASSWORD = getenv('MQTT_PASSWORD')

print("*"*50)
print(API_KEY, API_ENDPOINT, MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD)
print("-"*50)

# List of MQTT topics to subscribe to
topics = ['maticas-tech/numeric-data/#',
          'maticas-tech/image-data/#',]

# List of temporal MQTT messages, for later sending to the API
# as a big batch 
MAX_MESSAGES = 20
messages = []


# Define the callback function that will be called when a message is received
def on_message(client, userdata, message):
    print("Received message '" + str(message.payload.decode('utf-8')) + "' on topic '" + message.topic + "' with QoS " + str(message.qos))

    # split the topic into parts
    parts = message.topic.split('/')

    # ordering of the parts is important 
    # e.g. "maticas-tech/numeric-data/growing-zone1-id/variable-UIID/datetime-timezone-aware/"
    # 'datetime-timezone-aware' has pattern: 'YYYY-MM-DDTHH:MM:SS+HH:MM'
    parameters = {}
    parameters['crop'] = parts[2]
    parameters['variable'] = parts[3]
    parameters['datetime'] = parts[4]
    parameters['value'] = message.payload.decode('utf-8')

    # add the message to the list of messages
    if len(messages) < MAX_MESSAGES:
        messages.append(parameters)
    else:
        # send the messages to the API
        send_messages_to_api()

# Define the callback function that will be called when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):

    print("Connected with result code " + str(reason_code))
    if reason_code != 0:
        print("Failed to connect to the MQTT broker")
        return

    # Subscribe to the topics
    for topic in topics:
        client.subscribe(topic)

# Define the callback function that will be called when the client disconnects from the server.
# NEW code for both version
def on_disconnect(client, userdata, flags, reason_code, properties):
    print("Disconnected with result code " + str(reason_code))
    if reason_code == 0:
        # send the messages to the API
        send_messages_to_api()
    elif reason_code != 0:
        print("Unexpected disconnection.")


# Define the function that will send the messages to the API
def send_messages_to_api():
    print("Sending messages to the API")

    headers = {'Content-Type': 'application/json',
               'Authorization': 'Token ' + API_KEY}

    # send the messages to the API
    response = requests.post(API_ENDPOINT, headers = headers, data = json.dumps(messages))

    # print the response from the API
    print(response.text)

    # depending on the response, you may want to clear the messages list
    if response.status_code == 201:
        messages.clear()
    

# Create an MQTT client
client_id = "mqtt-api-bridge-123"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Assign the functions to the client
client.on_message = on_message
client.on_connect = on_connect
client.on_disconnect = on_disconnect

# Connect to the MQTT broker
if __name__ == "__main__":
    client.connect(MQTT_BROKER, MQTT_PORT)

    # Start the loop
    client.loop_forever()