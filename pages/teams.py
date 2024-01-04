import streamlit as st
import redis
import pandas as pd
import msgpack

stream_name = "auction:jpls5"

try:
    #df = st.session_state.df
    r = st.session_state.db
except Exception as e:
    print(e)
    st.info("Enter Admin Password to continue")
    st.stop()

if st.button("Refresh", use_container_width=True):
    # get df from redis db
    df = pd.DataFrame(msgpack.unpackb(r.get("new_df"), raw=False, strict_map_key=False))
    team_list = df["team"].tolist()
    team_points = df["present_points"].tolist()
    team_max_bid = df["max_bid_pp"].tolist()

    # Team points dashboard
    c = st.columns(3, gap="small")
    for team, points, max_bid in zip(team_list, team_points, team_max_bid):
        c[0].subheader(team)
        c[0].metric(":blue[Total Points]", points)
        c[1].subheader("🛎")
        c[1].metric(":blue[Max Bid Allowed]", int(max_bid))
else:
    st.info("Refresh to load data")
