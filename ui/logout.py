import streamlit as st


def render_logout():
    """Provide a logout button to clear the session state."""

    if st.button("Logout"):
        st.session_state.pop("user", None)
        st.rerun()
