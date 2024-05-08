import json
import requests
import paho.mqtt.client as paho

from os import getenv
from dotenv import load_dotenv

load_dotenv()
API_KEY = getenv('API_KEY')
API_ENDPOINT = getenv('API_ENDPOINT')
MQTT_BROKER = getenv('MQTT_BROKER')
MQTT_PORT = getenv('MQTT_PORT')
MQTT_USERNAME = getenv('MQTT_USERNAME')
MQTT_PASSWORD = getenv('MQTT_PASSWORD')

# List of MQTT topics to subscribe to
topics = []

# List of temporal MQTT messages, for later sending to the API
# as a big batch 
MAX_MESSAGES = 20
messages = []


# Define the callback function that will be called when a message is received
def on_message(client, userdata, message):
    print("Received message '" + str(message.payload) + "' on topic '" + message.topic + "' with QoS " + str(message.qos))

    # split the topic into parts
    parts = message.topic.split('/')

    # ordering of the parts is important 
    # e.g. "maticas-tech/growing-zone1-id/variable-UIID/datetime-timezone-aware/" will be split into
    # ['maticas-tech', 'growing-zone1-id', 'variable-UIID', 'datetime-timezone-aware']
    # 'datetime-timezone-aware' has pattern: 'YYYY-MM-DDTHH:MM:SS+HH:MM'
    parameters = {}
    parameters['crop'] = parts[1]
    parameters['variable'] = parts[2]
    parameters['datetime'] = parts[3]
    parameters['value'] = message.payload

    # add the message to the list of messages
    if len(messages) < MAX_MESSAGES:
        messages.append(parameters)
    else:
        # send the messages to the API
        send_messages_to_api()

# Define the callback function that will be called when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribe to the topics
    for topic in topics:
        client.subscribe(topic)

# Define the callback function that will be called when the client disconnects from the server.
def on_disconnect(client, userdata, rc):
    print("Disconnected with result code " + str(rc))

    # send the messages to the API
    send_messages_to_api()

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
client = paho.
