import streamlit as st

password = st.text_input("Enter Password", "password")

if password == st.secrets["admin"]:
    st.write("Admin Settings")