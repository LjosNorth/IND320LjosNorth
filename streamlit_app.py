import streamlit as st
from utils.UserRoles import UserRoles
from utils.decorators import *

#initiate role
if "userRole" not in st.session_state:
    st.session_state.userRole = UserRoles.VIEWER

@require_role(UserRoles.VIEWER)
def prage():
    print("you can see what a viewer can, pog")
prage()

''' Pages '''
pageHome = st.Page("pages/home.py", title="Home")
pageTables = st.Page("pages/tabularData.py", title="Tables")
pagePlots = st.Page("pages/plotData.py", title="Plots")
pageSettings = st.Page("pages/page4.py", title="settings")

if st.session_state.userRole == UserRoles.ADMIN:
    pages = [pageHome, pageTables, pagePlots, pageSettings]
else:
    pages = [pageHome, pageTables, pagePlots]

sidebar = st.navigation(pages, position="sidebar")
sidebar.run()