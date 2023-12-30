import streamlit as st
import pandas as pd
import redis
from threading import Thread
from streamlit.runtime.scriptrunner import add_script_run_ctx
import json
import time
from datetime import datetime

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
    readable_time = datetime.fromtimestamp(seconds)
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
if 'last_bid' not in st.session_state:
    st.session_state.last_bid = 100
if 'winning_team' not in st.session_state:
    st.session_state.winning_team = "START BIDDING"

st.header("Winning Bid")
c1, c2 = st.columns(2)
c1.write("Winning Team")
c1.subheader(f"{st.session_state.winning_team}")
c2.metric(label="Bid", value=f"{st.session_state.last_bid}")
st.divider()
co1, co2 = st.columns(2)
# refresh page for data to reload
co1.button("Refresh", use_container_width=True)
# delete all stream data
if co2.button("Reset", use_container_width=True):
    r.xtrim(stream_name, 0)

st.write("Received bids:")

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()
st.dataframe(st.session_state.data, use_container_width=True)
# FIXME: add rerun frontend code

def stream_listener(redis_client, stream_name, callback):
    while True:
        data = []
        messages = redis_client.xread({stream_name: 0}) #, count=10, block=0
        if messages:
            for message_id, fields in messages:
                for field_name, field_value in fields:
                    field_name_str = field_name.decode("utf-8")
                    timestamp = field_name_str.split("-")[0]
                    dt = ms_to_datetime(int(timestamp))
                    values = []
                    for key, value in field_value.items():
                        value_str = value.decode("utf-8")
                        values.append(value_str)
                    data.append({
                        'id': message_id.decode("utf-8"),
                        'timestamp': dt,
                        'team_name': values[0],
                        'bid': int(values[1])
                    })
                #callback(fields)
            # Create a DataFrame
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ns')
            df = df.set_index('timestamp')
            
            # add logic for choosing the best bid
            df_sorted = df.sort_values(by='bid', ascending=False)
            max_bid_index = df_sorted['bid'].idxmax()
            max_bid = df.loc[max_bid_index, 'bid']
            # FIXME: below code for cloud!
            try:
                max_bid_int = int(max_bid.iloc[0, 0])
            except:
                print("-----------error 1-----------")
                max_bid_int = max_bid
            # add logic to update dashboard with latest data
            try:
                if max_bid_int > st.session_state.last_bid:
                    st.session_state.winning_team = df.loc[max_bid_index, 'team_name']
                    st.session_state.last_bid = max_bid_int
            except:
                print("----------error 2---------")
                print(max_bid_int)
                print(type(max_bid_int), type(st.session_state.last_bid))
            
            print(df_sorted)
            st.session_state.data = df_sorted
            print("----------------------NEW----------------------")
            time.sleep(5)
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
        {"team": f"{team_name}", "bid": bid_amount},
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