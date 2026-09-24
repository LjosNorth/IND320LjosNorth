import streamlit as st
from utils import sessionstatehandler
from utils.UserRoles import UserRoles


# initiate needed sessionstate things
sessionstatehandler.SessionState()

 #Role Change Logic, for testing
with st.sidebar:
    st.write("Change Role")
    if st.session_state.userRole != UserRoles.ADMIN:
        if st.button("ADMIN"):
            st.session_state.userRole = UserRoles.ADMIN
            st.rerun()
    if st.session_state.userRole != UserRoles.USER:
        if st.button("USER"):
            st.session_state.userRole = UserRoles.USER
            st.rerun()
    if st.session_state.userRole != UserRoles.VIEWER:
        if st.button("VIEWER"):
            st.session_state.userRole = UserRoles.VIEWER
            st.rerun()

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