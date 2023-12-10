import streamlit as st
import pandas as pd

# Auction Dashboard
teams = pd.read_csv("data/teams.csv")
st.write(teams)