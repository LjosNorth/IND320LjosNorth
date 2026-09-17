import streamlit as st

st.set_page_config(
    page_title="lorem ipsum",
    page_icon="󰘁",
    layout="centered",
)

pageHome = st.Page("pages/page1.py",title="home")
pageTables = st.Page("pages/tabularData.py", title="Tables")
page3 = st.Page("pages/page3.py", title="page3")
pageSettings = st.Page("pages/page4.py", title="settings")

if st.session_state.get("is_admit", True):
    pages = [pageHome, pageTables, page3, pageSettings]
else:
    pages = [pageHome, pageTables, page3]

sidebar = st.navigation(pages, position="sidebar")
sidebar.run()