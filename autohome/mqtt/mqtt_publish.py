# python 3.6

import random
import time

from paho.mqtt import client as mqtt_client

# le_wagon_769
# autohome769

broker = 'test.mosquitto.org' #'broker.emqx.io'
port = 1883
topic = ""
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = ''
password = ''

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, topic='le_wagon_769', msg=''):
    print(msg)
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def run(topic='le_wagon_769', msg=''):
    client = connect_mqtt()
    client.loop_start()
    publish(client, topic, msg)


def send_msg(topic, msg):
    run(topic, msg)


if __name__ == '__main__':
    run()
