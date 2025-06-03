from data_managers import load_data, save_data,init_db

from frontend import submit_form, filter_data, display_table, download_excel, delete_records, edit_records
# from utils import all_members_done, send_email_with_excel
import streamlit as st

def main():
    st.set_page_config(page_title="Weekly Team Status", layout="wide")
    st.title("📋 Weekly Team Status Dashboard")

    # df = load_data()


    init_db()  # ✅ Ensure DB and table exist
    
    df = load_data()




    df, updated = submit_form(df)
    if updated:
        save_data(df)

    st.subheader("📊 Team Status Overview")
    if df.empty:
        st.info("No updates submitted yet. Use the form above to add your first update.")
    else:
        # Delete section
        df_new = delete_records(df)
        if len(df_new) != len(df):
            save_data(df_new)
            df = df_new
        
          # 🔁 Edit records section
        if "show_edit_records" not in st.session_state:
            st.session_state.show_edit_records = False

        edit_col1, edit_col2 = st.columns([1, 6])
        with edit_col1:
            if not st.session_state.show_edit_records:
                if st.button(" Show Edit Options"):
                    st.session_state.show_edit_records = True
            else:
                if st.button(" Hide Edit Options"):
                    st.session_state.show_edit_records = False

        if st.session_state.show_edit_records:
            df_updated = edit_records(df)
            if not df_updated.equals(df):
                save_data(df_updated)
                df = df_updated
        
        filtered_df = filter_data(df)
        display_table(filtered_df)
        download_excel(filtered_df)

        

if __name__ == "__main__":
    main()
