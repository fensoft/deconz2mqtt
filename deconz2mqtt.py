#!/usr/bin/env python 

import websocket, paho.mqtt.client, threading, requests, json, argparse, logging

logging.basicConfig(level=logging.DEBUG)
#websocket.enableTrace(True)

mqtt_logger = logging.getLogger('mqtt')
websocket_logger = logging.getLogger('websocket')

name2id = {}
id2name = {}

def flatten_json(nested_json, separator='/'):
  out = {}
  def flatten(x, name=''):
    if type(x) is dict:
      for a in x:
        flatten(x[a], name + a + separator)
    elif type(x) is list:
      i = 0
      for a in x:
        flatten(a, name + str(i) + separator)
        i += 1
    else:
      out[name[:-1]] = x
  flatten(nested_json)
  return out
    
def on_websocket_message(ws, message):
  websocket_logger.debug(message)
  msg = json.loads(message)
  if msg['t'] == 'event' and msg['e'] == 'changed':
    name = id2name[msg['r']][msg['id']]
    if 'state' in msg and 'id' != '1':
      for key, val in flatten_json(msg['state']).items():
        mqtt.publish("{}/{}/{}/state/{}".format(args.mqtt_prefix, msg['r'], name, key), val)
  else:
    websocket_logger.error('unhandled:' + msg)

def on_websocket_error(ws, error):
  websocket_logger.error(str(error))

def on_websocket_close(ws):
  websocket_logger.error("connection closed")

def on_websocket_open(ws):
  websocket_logger.error("connected to websocket")

def on_mqtt_connect(client, userdata, flags, rc):
  mqtt_logger.info("Connected to mqtt")
  for type in ['lights', 'sensors', 'groups', 'rules', 'schedules']:
    name2id[type] = {}
    id2name[type] = {}
    r = requests.get('{}/{}'.format(args.deconz_rest, type))
    for id, node in r.json().items():
      for key, val in flatten_json(node).items():
        mqtt.publish("{}/{}/{}/{}".format(args.mqtt_prefix, type, node['name'], key), val, retain=True)
        mqtt.publish("{}/{}/{}/id".format(args.mqtt_prefix, type, node['name']), id, retain=True)
        id2name[type][id] = node['name']
        name2id[type][node['name']] = id
  mqtt.subscribe("{}/#".format(args.mqtt_prefix))

def on_mqtt_message(client, userdata, msg):
  try:
    content = msg.topic.split('/')
    type = content[1]
    name = content[2]
    what = content[-2]
    value = msg.payload.decode('utf8')
    if value.lower() == "true":
      value = True
    elif value.lower() == "false":
      value = False
    if content[-1] == "set":
      if type == 'lights':
        if name in name2id[type]:
          requests.put('{}/lights/{}/state'.format(args.deconz_rest, name2id[type][name]), json={what: value})
        else:
          mqtt.error("{} not found".format(name))
      else:
        mqtt.error("type {} not handled".format(type))
  except:
    mqtt.error("error: {}".format(str(msg.payload)))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--deconz-websocket", dest="deconz_websocket", help="websocket url to deconz (ws://127.0.0.1:443)", required=True)
  parser.add_argument("--mqtt", help="mqtt ip (127.0.0.1)", required=True)
  parser.add_argument("--deconz-rest", dest="deconz_rest", help="deconz rest url (http://1270.0.0.1/api/KEY)", required=True)
  parser.add_argument("--mqtt-prefix", dest="mqtt_prefix", help="mqtt prefix", required=True)
  args = parser.parse_args()
  websocket = websocket.WebSocketApp(args.deconz_websocket, on_message = on_websocket_message, on_error = on_websocket_error, on_close = on_websocket_close, on_open = on_websocket_open)
  mqtt = paho.mqtt.client.Client()
  if ":" not in args.mqtt:
    mqtt.connect(args.mqtt.split(":")[0], 1883, 60)
  else:
    mqtt.connect(args.mqtt.split(":")[0], int(args.mqtt.split(":")[1]), 60)
  mqtt.on_connect = on_mqtt_connect
  mqtt.on_message = on_mqtt_message
  threading.Thread(target=lambda: websocket.run_forever()).start()
  threading.Thread(target=lambda: mqtt.loop_forever()).start()