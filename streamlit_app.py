import streamlit as st

st.set_page_config(
    page_title="lorem ipsum",
    page_icon="󰘁",
    layout="centered",
)

home = st.Page(
    "pages/page1.py",
    title="home"
)
page2 = st.Page(
    "pages/page2.py",
    title="page2"
)
page3 = st.Page(
    "pages/page3.py",
    title="page3"
)
settings = st.Page(
    "pages/page4.py",
    title="settings"
)

selected_page = st.navigation(
    [
        home,
        page2,
        page3,
        settings
    ],
    position="sidebar"
)

selected_page.run()