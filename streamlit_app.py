import streamlit as st

pageHome = st.Page("pages/home.py", title="Home")
pageTables = st.Page("pages/tabularData.py", title="Tables")
pagePlots = st.Page("pages/plotData.py", title="Plots")
pageSettings = st.Page("pages/page4.py", title="settings")

if st.session_state.get("is_admit", True):
    pages = [pageHome, pageTables, pagePlots, pageSettings]
else:
    pages = [pageHome, pageTables, pagePlots]

sidebar = st.navigation(pages, position="sidebar")
sidebar.run()