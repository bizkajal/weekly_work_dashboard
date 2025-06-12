import streamlit as st
import logging

from ui.login import render_login
from ui.logout import render_logout
from services.data_managers import init_db


def main_app():
    # Show logout button only if logged in
    if st.button("Logout"):
        render_logout()

    st.write("App content goes here...")


def init_session_state():
    defaults = {"logged_in": False, "username": "", "theme": "light", "user_data": None}
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def main():
    st.set_page_config(page_title="Weekly Team Status", layout="wide")
    # init database if tables are not present
    init_db()
    # initialize the session state...
    init_session_state()
    # Configure logging
    logging.basicConfig(
        format="%(asctime)s — %(levelname)s — %(message)s", level=logging.INFO
    )

    logger = logging.getLogger(__name__)
    if st.session_state.logged_in:
        logger.info("logged In state:{}".format(st.session_state.logged_in))
        main_app()
    else:
        render_login()

    return "something"


if __name__ == "__main__":
    main()
