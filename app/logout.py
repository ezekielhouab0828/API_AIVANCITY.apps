import streamlit as st

st.session_state.clear()
st.success("Déconnecté.")
st.switch_page("pages/login.py")