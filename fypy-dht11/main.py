import pycom
from dht import DTH
import time
from telenor import StartIoT
from mqtt import MQTTClient
from uos import urandom
from ujson import dumps
from time import sleep
import machine
import math
import network
import os
import utime
import gc
from network import LTE
#lte = LTE()
#lte.deinit()

## Configurations for the sensor
pycom.heartbeat(False)
pycom.rgbled(0x00001F) # blue

# MQTT configuration
MQTT_PORT = 1883
MQTT_HOST = 'hostname'                  # <--- ENTER HOST HERE
MQTT_USER = 'username'                  # <--- ENTER USERNAME HERE
MQTT_PASS = 'password'                  # <--- ENTER PASSWORD HERE

THING_ID = 'some-identifier'             # <--- ENTER YOUR NAME OR SOMETHING HERE
MQTT_TOPIC_SEND = 'iot/temp/send'        # <--- ENTER THE TOPIC TO SEND TO HERE
MQTT_TOPIC_RECE = 'iot/temp/receive'     # <--- ENTER THE TOPIC TO RECEIVE FROM HERE

# Define callback for when we receive messages
def sub_callback(topic, msg):
  print(msg)

# Init DHT11 sensor
dht = DTH('P23', sensor=0)
time.sleep(2)

gc.enable()

# init the LTE network
iot = StartIoT(network='lte-m')
# Connect to the network
print("Started connecting to the network...")
iot.connect()
pycom.rgbled(0x1F1F00) #yellow
# We should now be connected.
# Setup an MQTT client.
client = MQTTClient(
client_id=THING_ID, server=MQTT_HOST,
port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASS, keepalive=10000)

# Set callback function, connect, and subscribe to topic
client.set_callback(sub_callback)
client.connect()
client.subscribe(MQTT_TOPIC_RECE)
pycom.rgbled(0x1F001F) #Pink

while True:

    value = dht.read()
    if value.is_valid():
        # Create the MQTT data payload
        payload = {
            'env': {
            'temp': value.temperature,
            'hum': value.humidity
            },
            'mem-stats': gc.mem_free()
        }
        # Format payload as a JSON string
        json = dumps(payload)
        print("sending data: ",json)
        # Publish JSON string over the network
        client.publish(topic=MQTT_TOPIC_SEND, msg=json, qos=0)

    # Wait before running loop again
    time.sleep(15)
    # Check if we got a downlink message from the MQTT broker
    client.check_msg()