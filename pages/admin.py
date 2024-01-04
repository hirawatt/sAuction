import hmac
import streamlit as st
import pandas as pd
import msgpack

st.set_page_config("Admin Panel", layout="wide")

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
start_points = [10000, 10000, 13000, 15000]
present_points = start_points
bonus_points = [0, 0, 0, 0]
total_bonus_points = bonus_points
used_points = [0, 0, 0, 0]
total_used_points = used_points
# FIXME: calculate these
team_max_bid = [i*0.2 for i in present_points]

data = {
    "team": team_list,
    "start_points": start_points,
    "bonus_points": bonus_points,
    "total_bonus_points": total_bonus_points,
    "used_points": used_points,
    "total_used_points": total_used_points,
    "present_points": present_points,
    "max_bid_pp": team_max_bid
    }

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(data)

edited_df = st.data_editor(
    st.session_state.df,
    disabled=["total_bonus_points", "total_used_points", "present_points", "max_bid_pp"],
    column_config={
        "team": "Team Name",
        "start_points": "Starting Points",
        "bonus_points": "Bonus Points",
        "total_bonus_points": "Total BP",
        "used_points": "Used Points",
        "total_used_points": "Total UP",
        "present_points": "Present Points",
        "max_bid_pp": "Max Bid per Player",
    },
    num_rows="fixed", # FIXME: make this dynamic
    hide_index=True,
    use_container_width=True)

# Data Processing for updated df
def process_data(edited_df):
    edited_df["total_bonus_points"] = edited_df["total_bonus_points"] + edited_df["bonus_points"]
    edited_df["bonus_points"] = 0
    edited_df["total_used_points"] = edited_df["total_used_points"] + edited_df["used_points"]
    edited_df["used_points"] = 0
    edited_df["present_points"] = edited_df["start_points"] + edited_df["total_bonus_points"] - edited_df["total_used_points"]
    edited_df["max_bid_pp"] = [i*0.2 for i in edited_df["present_points"]]
    return edited_df

processed_df = process_data(edited_df)
#st.dataframe(processed_df, use_container_width=True, hide_index=True)

c1, c2, c3 = st.columns(3)
# Reset Data & Load Default DB Data
if c1.button("Reset to Default", use_container_width=True):
    df_retrieved = pd.DataFrame(msgpack.unpackb(r.get("default_df"), raw=False, strict_map_key=False))
    st.session_state.df = df_retrieved
    st.rerun()
    
c2.button("Refresh", use_container_width=True)
# Update Data to DB
if c3.button("Update Data", type="primary", use_container_width=True):
    st.session_state.df = processed_df
    # store df in redis db
    r.set("new_df", msgpack.packb(processed_df.to_dict(), use_bin_type=True))
    df_retrieved = pd.DataFrame(msgpack.unpackb(r.get("new_df"), raw=False, strict_map_key=False))
    with st.expander("Data"):
        st.dataframe(df_retrieved, use_container_width=True)
    st.rerun()