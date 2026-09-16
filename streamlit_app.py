import streamlit as st

st.set_page_config(
    page_title="First App",
    page_icon="󰘁",
    layout="centered",
)

st.title("First App")
st.write("Welcome")

name = st.text_input("Enter Name: ")
if name:
    st.success(f"Name: {name}")