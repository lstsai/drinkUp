"""EE 250L Lab 04 Starter CodemailboxTools
demo link:https://drive.google.com/file/d/1I_riVtSSz6xbTCH55Dq6wnpbjYuDo1Hb/view?usp=sharing
github: https://github.com/usc-ee250-fall2020/lab05-lab5_/tree/lab05
Run rpi_pub_and_sub.py on your Raspberry Pi."""

import paho.mqtt.client as mqtt
import time
from datetime import datetime
from influxdb import InfluxDBClient
import grovipi
class waterSensor():
    sendLevel=True
    maxLevel=10
    minLevel=5
    influxclient=None
    currReading=1
    def connectInflux(self):
        self.influxclient = InfluxDBClient(host='18.219.103.221', port=8086, database='waterSensor')
        self.influxclient.create_database('waterSensor')
    def sendReading(self):
        json_body = [
            {
                "measurement": "levels",
                "tags": {
                    "host": "server01",
                    "region": "us-west"
                },
                "time": datetime.now(),
                "fields": {
                    "waterLevel": self.currReading
                }
            }
        ]
        self.influxclient.write_points(json_body)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to server (i.e., broker) with result code "+str(rc))

        #subscribe to topics of interest here
        client.subscribe('lstsai/waterCtrl')#sub to led and set custom callback
        client.message_callback_add('lstsai/waterCtrl', self.waterCtrl_callback)
        
        client.subscribe('lstsai/maxLevel')#sub to led and set custom callback
        client.message_callback_add('lstsai/maxLevel', self.maxLevel_callback)

        client.subscribe('lstsai/minLevel')#sub to led and set custom callback
        client.message_callback_add('lstsai/minLevel', self.minLevel_callback)

    def waterCtrl_callback(self,client, userdata, msg):
        if str(msg.payload, "utf-8")=="start":
            self.sendLevel=True
        elif str(msg.payload, "utf-8")=="stop":
           self.sendLevel=False

    def maxLevel_callback(self, client, userdata, msg):
        self.maxLevel=int(str(msg.payload, "utf-8"))

    def minLevel_callback(self, client, userdata, msg):
        self.minLevel=int(str(msg.payload, "utf-8"))
    
    #Default message callback. Please use custom callbacks.
    def on_message(self, client, userdata, msg):
        print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

    def main(self):
        client = mqtt.Client()
        client.on_message = self.on_message
        client.on_connect = self.on_connect
        client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
        client.loop_start()

        self.connectInflux()
         #set the ports
        ranger= 4
        ledMax= 2
        ledMin= 3
        reading =1
        lastReading=grovepi.ultrasonicRead(ranger)
        lastReading=1
        while True:
            self.currReading= grovepi.ultrasonicRead(ranger)
            if abs(self.currReading-lastReading)<5:
                self.sendReading()
                client.publish("lstsai/waterLevel", self.currReading)
                lastReading=self.currReading
            if self.sendLevel:
                self.sendReading()
            if self.currReading>self.maxLevel:
                grovepi.digitalWrite(ledMax, 1)
            else:
                grovepi.digitalWrite(ledMax, 0)
            if self.currReading<self.minLevel:
                grovepi.digitalWrite(ledMin, 1)
            else:
                grovepi.digitalWrite(ledMin, 0)

            time.sleep(1)
            
if __name__ == '__main__':
    waterS= waterSensor()
    waterS.main()
   