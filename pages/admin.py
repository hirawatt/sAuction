import hmac
import streamlit as st
import pandas as pd

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

# FIXME: make this data dynamic from db
df = pd.DataFrame([["Team 1", "10000", "10000", "500", "0"], ["Team 2", "12000", "12000", "600", "0"]], columns=["Teams", "Starting Points", "Present Points", "Max Bid per Player", "Bonus Points"])

edited_df = st.data_editor(
    df,
    disabled=["Starting Points", "Teams", "Max Bid per Player"],
    hide_index=True,
    use_container_width=True)

#st.write(edited_df)