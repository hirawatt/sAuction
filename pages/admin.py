import hmac
import streamlit as st
import pandas as pd
import msgpack

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Admin Panel Access
st.header("Admin Settings")
try:
    r = st.session_state.db
except Exception as e:
    print(e)
    st.info("Contact Admin/Go to Dashboard & return to this page")
    st.stop()

# FIXME: make this data dynamic from db
team_list = ["Team 1", "Team 2", "Team 3", "Team 4"]
team_points = [10000, 10000, 13000, 15000]
bonus_list = [0, 0, 0, 0]
# FIXME: calculate these
team_max_bid = [i/20 for i in team_points]
present_points = team_points

data = {"team": team_list, "start_points": team_points, "bonus": bonus_list, "present_points": present_points, "max_bid_pp": team_max_bid}
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(data)

df = st.session_state.df
edited_df = st.data_editor(
    df,
    disabled=["start_points", "team", "max_bid_pp"],
    column_config={
        "team": "Team Name",
        "start_points": "Starting Points",
        "bonus": st.column_config.NumberColumn(
            "Bonus Points",
            help="How much do you like this command (1-5)?",
            min_value=0,
            max_value=5000,
            step=1000,
            format="%d ⭐",
            ),
        "present_points": "Present Points",
        "max_bid_pp": "Max Bid per Player",
    },
    num_rows="dynamic",
    hide_index=True,
    use_container_width=True)

if st.button("Update Data"):
    # store df in redis db
    r.set("default_df", msgpack.packb(edited_df.to_dict(), use_bin_type=True))
    df_retrieved = pd.DataFrame(msgpack.unpackb(r.get("default_df"), raw=False, strict_map_key=False))
    with st.expander("Data"):
        st.dataframe(df_retrieved, use_container_width=True)
