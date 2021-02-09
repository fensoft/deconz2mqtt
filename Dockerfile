FROM ubuntu:bionic
RUN apt-get update; apt-get install -y python3-pip
ADD deconz2mqtt.py /app/deconz2mqtt.py
ADD requirements.txt /app/requirements.txt
RUN cd /app; pip3 install -r requirements.txt
ENV DECONZ_WEBSOCKET=ws://deconz:443
ENV MQTT_IP=mqtt
ENV DECONZ_REST=http://deconz/api/KEY
ENV MQTT_PREFIX=zigbee
CMD python3 /app/deconz2mqtt.py --deconz-websocket $DECONZ_WEBSOCKET --mqtt $MQTT_IP --deconz-rest $DECONZ_REST --mqtt-prefix $MQTT_PREFIX
