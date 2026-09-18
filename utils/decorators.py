import streamlit as st

from utils.UserRoles import UserRoles
pass

#decorator to limit what is seen to those roles meant to see it
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
