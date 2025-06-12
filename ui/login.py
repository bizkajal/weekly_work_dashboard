import streamlit as st
from ui.admin_dashboard import render_admin_dashboard
from ui.dashboard import render_dashboard
from services.data_managers import add_user, get_users, init_db
from services.data_managers import check_if_admin_login

# Initialize the database
init_db()


def show_login_page(login_tab):
    with login_tab:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                users = get_users()
                if username in users and users[username] == password:
                    st.session_state.user = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")


def show_singup_page(signup_tab):
    with signup_tab:
        new_user = st.text_input("New Username", key="signup_user")
        new_pass = st.text_input("New Password", type="password", key="signup_pass")

        if st.button("Sign Up"):
            if not new_user or not new_pass:
                st.error("Please enter both username and password to sign up.")
            else:
                if add_user(new_user, new_pass):
                    st.success("User created successfully. Please log in.")
                else:
                    st.warning("Username already exists.")


def render_login():
    """Display the login and signup interface for users to authenticate or create an account."""

    # render specific user dashboard
    if "user" in st.session_state:
        # render admin dashboard
        admin_login = check_if_admin_login(st.session_state["user"])
        if admin_login:
            render_admin_dashboard()
            return
        else:
            # render user dashboard
            render_dashboard()
            return

    st.title("Login")
    login_tab, signup_tab = st.tabs([" Login", " Sign Up"])

    # --- Login Tab ---
    show_login_page(login_tab)
    # --- Signup Tab ---
    show_singup_page(signup_tab)
