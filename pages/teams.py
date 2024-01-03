import streamlit as st
import redis

stream_name = "auction:jpls5"

st.header("Team Auction Points")

r = st.session_state.db
st.write(r)