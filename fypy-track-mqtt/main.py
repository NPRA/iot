#If for some reason it still doesn work you could try to “reset” the modem by issuing the following commands in the REPL:
#from network import LTE
#lte = LTE()
#lte.deinit()
#lte.init()
#lte.attach(apn="telenor.iot", band=20)
#
#You can then check if the device is attached with the following line:
#lte.isattached()
#
#It should return True if the modem is attached to the network.


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
from machine import RTC
# Her har Tomas hacka litt
#from L76GNSS import L76GNSS
from pytrack import Pytrack
from L76GNSV4 import L76GNSS


# Imports for sensor
import time
import pycom
from machine import Pin

## Configurations for the sensor
pycom.heartbeat(False)
pycom.rgbled(0x00001F) # blue


# MQTT configuration
MQTT_PORT = 1883
MQTT_HOST = 'hostname'                  # <--- ENTER HOST HERE
MQTT_USER = 'username'                  # <--- ENTER HOST HERE
MQTT_PASS = 'password'                  # <--- ENTER HOST HERE

THING_ID = 'some-identifier'             # <--- ENTER YOUR NAME OR SOMETHING HERE
MQTT_TOPIC_SEND = 'iot/temp/send'        # <--- ENTER THE TOPIC TO SEND TO HERE
MQTT_TOPIC_RECE = 'iot/temp/receive'     # <--- ENTER THE TOPIC TO RECEIVE FROM HERE

def sub_callback(topic, msg):
  print(msg)

def run():

  gc.enable()
  py = Pytrack()
  L76 = L76GNSS(pytrack=py)
  L76.setAlwaysOn()
  print("Waiting for GPS to come online...")
  L76.get_fix(debug=False)
  print("GPS is online")

  # Create a new Telenor Start IoT object using the LTE-M network.
  # Change the `network` parameter if you want to use the NB-IoT
  # network like this: iot = StartIoT(network='nb-iot')
  # You must flash the correct Sequans modem firmware before
  # changing network protocol!
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

  # Set callback function, connect, and subscribe to MIC Thing topic
  client.set_callback(sub_callback)
  client.connect()
  client.subscribe(MQTT_TOPIC_RECE)
  pycom.rgbled(0x1F001F) #Pink
  # Start an endless loop and publish some dummy data over MQTT.
  while True:

    #try:
    # Generate random data (Delete/comment out these lines once you activate the sensor readings)
    coord = L76.coordinates()
    print(coord)


    # Create the MQTT data payload
    payload = {
      'pos': {
        'lat': coord['latitude'],
        'lon': coord['longitude']
      },
      'mem-stats': gc.mem_free()
    }
    

    # Format payload as a JSON string
    json = dumps(payload)

    if coord['latitude'] != None:
      print('Sending data:', json)

      # Publish JSON string over the network
      client.publish(topic=MQTT_TOPIC_SEND, msg=json, qos=0)
      pycom.rgbled(0x001F00) #Green
    else:
      print('no gps fix yet, waiting')

    # Handle exception (if an error occured)
    #except Exception as e:
    #  print('Caught exception:', e)
    #  pycom.rgbled(0x1F0000) #Red

    # Wait 10 seconds before running loop again
    sleep(15)

    # Check if we got a downlink message from the MQTT broker
    client.check_msg()

# The example code will start here
print('Running example code...')
run()
