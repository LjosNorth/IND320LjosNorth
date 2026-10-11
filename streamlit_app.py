'''
Main streamlit loader. Handles init, sidebar and other logic
'''

import streamlit as st
from zmq.backend import select

from utils import sessionstatehandler
from utils.UserRoles import UserRoles


# initiate needed sessionstate things
sessionstatehandler.SessionState()

st.markdown("""
    <style>
    [data-testid="stSelectbox"] {
        margin-top: -15px;
        margin-bottom: -10px;
    }
    </style>
""", unsafe_allow_html=True)

#Role Change Logic, this does not need to exist, I'm just bored
with st.sidebar:
    userSelect = [role.name for role in UserRoles]
    st.caption("User Role")
    roleSelect = st.selectbox("User Role", userSelect, width=100, placeholder="Select a role...", label_visibility="collapsed")
    st.session_state.userRole = UserRoles[roleSelect]


# Pages
pageHome = st.Page("pages/home.py", title="Home")
pageTables = st.Page("pages/tabularData.py", title="Tables")
pagePlots = st.Page("pages/plotData.py", title="Plots")
pageSettings = st.Page("pages/settings.py", title="settings")

# who sees what pages
if st.session_state.userRole == UserRoles.ADMIN:
    pages = [pageHome, pageTables, pagePlots, pageSettings]
else:
    pages = [pageHome, pageTables, pagePlots]

# make and run sidebar
sidebar = st.navigation(pages, position="sidebar")
sidebar.run()