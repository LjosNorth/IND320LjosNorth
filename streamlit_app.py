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

histTarget=['USER', 'VIEWER', 'ADMIN', 'USER']
def changedRole():
    if histTarget != st.session_state.roleHist and len(st.session_state.roleHist)<5:
        st.session_state.roleHist.append(st.session_state.roleSelectBox)

#Role Change Logic, this does not need to exist, I'm just bored
with st.sidebar:
    userSelect = [role.name for role in UserRoles]
    if histTarget != st.session_state.roleHist:
        userSelect.pop(-1)
    st.caption("User Role")
    roleSelect = st.selectbox("User Role", userSelect, width=100, placeholder="Select a role...", label_visibility="collapsed", on_change=changedRole, key="roleSelectBox")
    st.session_state.userRole = UserRoles[roleSelect]
    st.caption(
        '''
        Feel free to ignore this "user role" thing, its primarily a "For Fun" thing im playing with
        '''
    )

# Pages
pageHome = st.Page("pages/home.py", title="Home", icon="🏠")
pageTables = st.Page("pages/tabularData.py", title="Tables", icon="🗒️")
pagePlots = st.Page("pages/plotData.py", title="Plots", icon="📊")
pageTransmission = st.Page("pages/transmissionsPlot.py", title="Transmission Plots", icon="📈")
pageSettings = st.Page("pages/settings.py", title="settings", icon="⚙️")

# who sees what pages
if st.session_state.userRole == UserRoles.ADMIN:
    pages = [pageHome, pageTables, pagePlots, pageTransmission, pageSettings]
else:
    pages = [pageHome, pageTables, pagePlots, pageTransmission]

# make and run sidebar
sidebar = st.navigation(pages, position="sidebar")
sidebar.run()