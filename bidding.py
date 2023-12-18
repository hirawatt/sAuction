import streamlit as st
import pandas as pd

st.markdown("<h1 style='text-align: center; color: blue;'>Bidding Portal</h1>", unsafe_allow_html=True)
# add 3 digit login code to enter
team_list = pd.read_csv("./data/redis-team.csv")
team_creds_list = team_list['Creds'].tolist()

# Main Bidding Logic

def bid():
    amount = st.number_input("Bid Amount", value=100, step=100, min_value=100, label_visibility="collapsed")
    st.button("Bid", use_container_width=True, type="primary")


    # FIXME: add button logic
    co1, co2 = st.columns(2)
    co1.button("Exit bid", use_container_width=True)
    co2.button("Refresh", use_container_width=True)

    # TODO: add logic to bid success
    bid_success = True
    if bid_success:
        st.toast(f'Bid for {amount} was successfull!', icon='✅')
    else:
        st.toast(f'Bid for {amount} unsuccessfull!', icon='❌')


# Login Check Screen
login_code = st.text_input("Enter code:")
if login_code:
    try:
        team_index = team_creds_list.index(int(login_code))
        team_name = team_list['Team'][team_index]
        st.subheader(f"Welcome {team_name},")
        bid()
    except:
        st.warning("Incorrect Code. Try again")