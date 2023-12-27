import streamlit as st
import pandas as pd
import redis
import threading
import json
import time

r = redis.Redis(
    host=st.secrets['redis']['host'],
    port=st.secrets['redis']['port'],
    password=st.secrets['redis']['password'])

stream_name = "auction:jpls5"

# Auction Dashboard
#data = r.xread(streams={"auction:jpls5": 0}, count=10, block=300)
st.write("Received messages:")
data = st.empty()

def stream_listener(redis_client, stream_name, callback):
    while True:
        messages = redis_client.xread({stream_name: ">"}, count=10, block=0)
        if messages:
            for message in messages[0][1]:
                callback(message)
        time.sleep(0.1)  # Adjust sleep time as needed

def process_message(message):
    data = message['fields']
    # Do something with the data
    data.text(data)
    print(data)

thread = threading.Thread(target=stream_listener, args=(r, stream_name, process_message))
thread.start()

# FIXME: testing : publish data
def publish_message(data):
    message = json.dumps(data)
    r.publish("auction:jpls5", message)

if st.button("Publish Message"):
    publish_message({"message": "Hello from Streamlit!"})