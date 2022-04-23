from autohome.mqtt import mqtt_publish

client = mqtt_publish.connect_mqtt()
client.loop_start()

mqtt_publish.publish(client, topic='le_wagon_769', msg='Testeeeeeeee')
