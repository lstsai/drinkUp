"""EE 250L Lab 04 Starter Code
demo link:https://drive.google.com/file/d/1I_riVtSSz6xbTCH55Dq6wnpbjYuDo1Hb/view?usp=sharing
github: https://github.com/usc-ee250-fall2020/lab05-lab5_/tree/lab05
Run rpi_pub_and_sub.py on your Raspberry Pi."""

import paho.mqtt.client as mqtt
import time

class waterTracker():
    valid_commands = ['quit', 'q', 'getLevel', 'setMax', 'setMin', 'startSending', 'stopSending' ]
    currWaterLevel=0
    maxLevel=10
    minLevel=5
    def command_is_valid(self, command):
        if command in self.valid_commands:
            return True
        else:
            print('Valid commands are {}'.format(self.valid_commands))
            return False

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to server (i.e., broker) with result code "+str(rc))
        #subscribe to topics of interest here
        client.subscribe('lstsai/waterLevel')#sub to led and set custom callback
        client.message_callback_add('lstsai/waterLevel', self.water_callback)

    def water_callback(self, client, userdata, msg):
        self.currWaterLevel=str(msg.payload, "utf-8")
        #print(str(msg.payload, "utf-8"))

    #Default message callback. Please use custom callbacks.
    def on_message(self, client, userdata, msg):
        print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))


    def main(self):
        client = mqtt.Client()
        client.on_message = self.on_message
        client.on_connect = self.on_connect
        client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
        client.loop_start()
        usr_input = ''
        command = ''

        while command != 'quit' and command != 'q':
            while not self.command_is_valid(usr_input):
                usr_input = input('Command: ')
                command = usr_input
            if command == 'getLevel':
                print("The current water level is "+str(self.currWaterLevel)+"cm")

            if command == 'setMax':
                maxL=int(input('Maximum Level: '))
                if(maxL <self.minLevel):
                    print("Maximum Level lower than Minimum Level")
                else:
                    client.publish("lstsai/maxLevel", maxL)
            if command == 'setMin':
                minL=int(input('Minimum Level: '))
                if(minL >self.maxLevel):
                    print("Minimum Level cannot be higher than Maximum Level")
                else:
                    client.publish("lstsai/minLevel", minL)
            if command == 'startSending':
                client.publish("lstsai/waterCtrl", 'start')
            if command == 'stopSending':
                client.publish("lstsai/waterCtrl", 'stop')

            usr_input = ''
        return 0

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    waterTracker= waterTracker()
    waterTracker.main()
