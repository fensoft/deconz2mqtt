# deCONZ2MQTT

This is a Python 3 project that acts as a bridge between deCONZ' websocket and MQTT. It connects to the Websocket of deCONZ and forward-publishes the messages via MQTT.

## Getting started

The Python script uses the following command-line arguments: 

`--deconz-websocket`
:   A fully qualified URL to the deCONZ host and web service, like `ws://192.168.178.101:81`

`--mqtt`
:   The host name or IP address of the MQTT server/broker

`--deconz-rest`
:   A fully qualified URL to the deCONZ HTTP API including the API key, like `http://deconz/api/KEY`

`--mqtt-prefix`
:   The root topic prefix for the MQTT topic names


### Using python

If you have installed Python (3) already, install its dependencies by running `pip3 install -r requirements.txt`. Afterwards simply run it using the following command:

```bash
python3 deconz2mqtt.py \
  --deconz-websocket $DECONZ_WEBSOCKET \
  --mqtt $MQTT_IP \ 
  --deconz-rest $DECONZ_REST \
  --mqtt-prefix $MQTT_PREFIX
```

### Using Docker

Adjust the ENV vars in the `Dockerfile` accordingly (see above) and `docker build` it.
