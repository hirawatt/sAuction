import streamlit as st
import pandas as pd
import redis
from threading import Thread
from streamlit.runtime.scriptrunner import add_script_run_ctx
import json
import time
import datetime
import numpy as np

# streamlit
st.set_page_config(
    'Smart Auction Portal',
    '🪙',
    layout='centered',
    initial_sidebar_state='collapsed',
    menu_items={
        "Get Help": "https://sauction.streamlit.app",
        "About": "Auction Portal App",
    },
)

def ms_to_datetime(milliseconds):
    seconds = milliseconds / 1000
    readable_time = datetime.datetime.fromtimestamp(seconds)
    formatted_time = readable_time.strftime("%H:%M:%S.%f") #%Y-%m-%d
    return formatted_time

@st.cache_resource
def get_database_session():
    # Create a database session object that points to the URL.
    r = redis.Redis(
        host=st.secrets['redis']['host'],
        port=st.secrets['redis']['port'],
        password=st.secrets['redis']['password'])
    return r

r = get_database_session()

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
st.button("Refresh", use_container_width=True)

st.write("Received bids:")

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()
st.write(st.session_state.data)
# FIXME: add rerun/refresh frontend code

def stream_listener(redis_client, stream_name, callback):
    while True:
        data = []
        messages = redis_client.xread({stream_name: 0}) #, count=10, block=0
        if messages:
            for message_id, fields in messages:
                for field_name, field_value in fields:
                    field_name_str = field_name.decode("utf-8")
                    ms = field_name_str.split("-")[0]
                    datetime = np.datetime64(ms, 'ns')
                    values = []
                    for key, value in field_value.items():
                        value_str = value.decode("utf-8")
                        values.append(value_str)
                    data.append({
                        'id': message_id.decode("utf-8"),
                        'timestamp': datetime,
                        'team_name': values[0],
                        'bid': values[1]
                    })
                #callback(fields)
            # Create a DataFrame
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            print(df)
            st.session_state.data = df
            print("----------------------NEW----------------------")
            time.sleep(1)
        else:
            print("No messages found in the stream.")

# Do something with the data
def process_message(fields):
    print(fields)

#stream_listener(r, stream_name, process_message)
t = Thread(target=stream_listener, args=(r, stream_name, process_message))
add_script_run_ctx(t)
t.start()

# testing
def send_bid(auction_name, team_name, bid_amount):
    resp = r.xadd(
        f"auction:{auction_name}",
        {"team": f"{team_name}", "bid": f"{bid_amount}"},
    )
    return resp # >>> 1692629613374-0

st.divider()
if st.button("Test Bid"):
    # bidding data
    auction_name = "jpls5"
    team_name = "Team 1"
    bid_amount = 200
    resp = send_bid(auction_name, team_name, bid_amount)
    st.write(resp)