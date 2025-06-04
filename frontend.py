import streamlit as st
import pandas as pd
from datetime import date
from data_managers import  save_data, load_data, init_db
import io

def submit_form(df, current_user):

    """Submit a new weekly update form for the current user."""

    with st.form(key=f"weekly_update_form_{current_user}_{len(df)}"):
        task = st.text_area("Task")
        status = st.selectbox("Status", ["In Progress", "Completed", "Blocked"])
        start_date = st.date_input("Start Date")
        eta = st.date_input("ETA")
        remarks = st.text_area("Remarks")
        submitted = st.form_submit_button("Submit")

        if submitted:
            new_entry = {
                "name": current_user,
                "task": task,
                "status": status,
                "start_date": str(start_date),
                "eta": str(eta),
                "remarks": remarks
            }

            # Append new entry
            full_df = load_data()
            full_df = pd.concat([full_df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(full_df)

            st.success(" Entry submitted successfully!")
            st.rerun() 
          

    return df





def display_table(df, current_user):

    """Display the team status overview table with options to edit or delete records."""

    st.subheader(" Team Status Overview")

    if df.empty:
        st.info("No records to display yet.")
        return df

    # --- Add column headers ---
    header_cols = st.columns([2, 2, 1.5, 1.5, 1.5, 2, 1.2, 1.2])
    headers = ["Name", "Task", "Status", "Start Date", "ETA", "Remarks"]
    for col, header in zip(header_cols, headers):
        col.markdown(f"**{header}**")  # Display header bold

    # --- Loop through rows ---
    for i, row in df.iterrows():
        cols = st.columns([2, 2, 1.5, 1.5, 1.5, 2, 1.2, 1.2])
        cols[0].write(row["name"])
        cols[1].write(row["task"])
        cols[2].write(row["status"])
        cols[3].write(row["start_date"])
        cols[4].write(row["eta"])
        cols[5].write(row["remarks"])

        can_edit = (current_user == "admin") or (row["name"] == current_user)
        can_delete = can_edit

        if can_edit and cols[6].button("Edit", key=f"edit_{i}"):
            st.session_state.edit_row_index = i
            st.rerun()

        if can_delete and cols[7].button("Delete", key=f"delete_{i}"):
            df = df.drop(index=i).reset_index(drop=True)
            save_data(df)
            st.success(" Record deleted!")
            st.rerun()

    return df


# --- Edit record form ---
def edit_record(df, idx, current_user):

    """Edit an existing record in the team status overview."""

    st.subheader("Edit Record")
    row = df.loc[idx]
    with st.form("edit_form"):
        name = st.text_input("Name", value=row["name"], disabled=current_user != "admin")
        task = st.text_area("Task", value=row["task"])
        status = st.selectbox("Status", ["In Progress", "Completed", "Blocked"], index=["In Progress", "Completed", "Blocked"].index(row["status"]))
        start_date = st.date_input("Start Date", value=pd.to_datetime(row["start_date"]).date())
        eta = st.date_input("ETA", value=pd.to_datetime(row["eta"]).date())
        remarks = st.text_area("Remarks", value=row["remarks"])

        if st.form_submit_button("Update Record"):
            df.loc[idx] = [name, task, status, start_date.strftime("%Y-%m-%d"), eta.strftime("%Y-%m-%d"), remarks]
            save_data(df)
            st.success("Record updated!")
            st.session_state.edit_row_index = None
            st.rerun()



def download_excel(df):

    """Download the team status overview as an Excel file."""
    
    import io
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    st.download_button(
        label="Download Excel",
        data=processed_data,
        file_name="weekly_team_status.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )