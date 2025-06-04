import streamlit as st
from login import show_login, logout
from data_managers import init_db, load_data, save_data,get_users, add_user
from frontend import submit_form, display_table, edit_record, download_excel

def main():
    st.set_page_config(page_title="Weekly Team Status", layout="wide")
    init_db()
    
    users = get_users()
    if "admin" not in users:
        add_user("admin", "admin")

  

    if "user" not in st.session_state:
        show_login()
        return
    


    current_user = st.session_state.user
    st.title(f"📋 Weekly Team Status - {current_user}")

    full_df = load_data()

    if current_user != "admin":
        view_df = full_df[full_df["name"] == current_user].reset_index(drop=True)
        # st.info("You can only view and modify your own records.")
        # Show form only for non-admin
        full_df = submit_form(full_df, current_user)
    else:
        view_df = full_df
        st.info("You can view all records.")

    view_df = display_table(view_df, current_user)

    if "edit_row_index" in st.session_state and st.session_state.edit_row_index is not None:
        edit_record(full_df, st.session_state.edit_row_index, current_user)

    if current_user == "admin":
        download_excel(full_df)

    logout()

if __name__ == "__main__":
    main()
