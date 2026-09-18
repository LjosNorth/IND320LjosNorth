import streamlit as st

from utils.UserRoles import UserRoles
pass


def require_role(required_role):
    def decorator(func):
        def wrapper(*args, **kwargs):
            userRole = st.session_state.userRole
            if userRole.value >= required_role.value:
                return func(*args, **kwargs)
            else:
                pass
        return wrapper
    return decorator
