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


# st.title("lorem ipsum")
# st.write("dolor sit amet, consectetur adipiscing elit. Integer enim neque, tincidunt eu sagittis a, suscipit ac eros. Vivamus vitae porttitor lorem, id fringilla dolor. Phasellus semper eu lacus a sodales")
