import streamlit as st
from utils.UserRoles import UserRoles

# Initiates all my needed session state thingies
class SessionState:
    def __init__(self):
        # initiate role
        if "userRole" not in st.session_state:
            st.session_state.userRole = UserRoles.VIEWER
        # initiate plotmonths
        if "plotMonths" not in st.session_state:
            st.session_state.plotMonths = 1