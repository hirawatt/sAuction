import streamlit as st
import redis

stream_name = "auction:jpls5"
r = st.session_state.db

#st.header("Team Auction Points")
# FIXME: make this dynamic from DB
team_list = ["Team 1", "Team 2", "Team 3", "Team 4"]
team_points = [10000, 10000, 13000, 15000]
team_max_bid = [i/20 for i in team_points]

# Team points dashboard
c1, c2, c3 = st.columns(3, gap="small")
for team, points, max_bid in zip(team_list, team_points, team_max_bid):
    c1.subheader(team)
    c1.metric("Total Points", points)
    c2.subheader("🛎")
    c2.metric("Max Bid Allowed", int(max_bid))