import streamlit as st
from data_managers import add_user, get_users, init_db

# Initialize the database
init_db()

def show_login():
    st.title("Login")
    login_tab, signup_tab = st.tabs(["🔐 Login", "📝 Sign Up"])

    # --- Login Tab ---
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

    # --- Signup Tab ---
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

def logout():
    if st.button("Logout"):
        st.session_state.pop("user", None)
        st.rerun()
