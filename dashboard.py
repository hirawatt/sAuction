import streamlit as st
import pandas as pd
import redis
import threading
import json
import time
import datetime

def ms_to_datetime(milliseconds):
    seconds = milliseconds / 1000
    readable_time = datetime.datetime.fromtimestamp(seconds)
    formatted_time = readable_time.strftime("%H:%M:%S.%f") #%Y-%m-%d
    return formatted_time

r = redis.Redis(
    host=st.secrets['redis']['host'],
    port=st.secrets['redis']['port'],
    password=st.secrets['redis']['password'])

# Auction Dashboard
# FIXME: make this dynamic
stream_name = "auction:jpls5"
last_bid = 1000
winning_team = "Team 1"

st.header("Winning Bid")
c1, c2 = st.columns(2)
c1.write("Winning Team")
c1.subheader(f"{winning_team}")
c2.metric(label="Bid", value=f"{last_bid}")
st.divider()

st.write("Received bids:")
test_data = r.xread({stream_name: 0})
if test_data:
    for message_id, fields in test_data:
        #st.write(f"Message ID: {message_id}")
        co1, co2, co3 = st.columns(3)
        for field_name, field_value in fields:
            field_name_str = field_name.decode("utf-8")
            #st.write(field_value.values())
            # convert millisecond data to readble format
            ms = field_name_str.split("-")[0]
            co1.write(ms_to_datetime(int(ms)))
            values = []
            for key, value in field_value.items():
                key_str = key.decode("utf-8")
                value_str = value.decode("utf-8")
                values.append(value_str)
            co2.write(values[0])
            co3.write(values[1])
            #st.write(f"- {field_name_str}: {field_value}")
else:
    st.write("No messages found in the stream.")

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
    print(data)

thread = threading.Thread(target=stream_listener, args=(r, stream_name, process_message))
thread.start()

# testing
def add_to_stream(auction_name, team_name, bid_amount):
    res3 = r.xadd(
        f"auction:{auction_name}",
        {"team": f"{team_name}", "bid": f"{bid_amount}"},
    )
    return res3 # >>> 1692629613374-0

# bidding data
auction_name = "jpls5"
team_name = "Team 1"
bid_amount = 200

if st.button("Test Bid"):
    resp = add_to_stream(auction_name, team_name, bid_amount)
    st.write(resp)