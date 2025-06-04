import streamlit as st
import pandas as pd
from datetime import date
from data_managers import  save_data, load_data, init_db
import io



def submit_form(df, current_user):
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

            # 🟢 Load full dataset and append new entry
            full_df = load_data()
            full_df = pd.concat([full_df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(full_df)

            st.success("Entry submitted successfully!")
            st.rerun()  # To refresh form and table
            return full_df

    return df


# --- Display and edit table ---
def display_table(df, current_user):
    st.subheader("Team Status Overview")
    for i, row in df.iterrows():
        cols = st.columns([2, 2, 1.5, 1.5, 1.5, 2, 1.5, 1.5])
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
            # df = df.drop(row.name).reset_index(drop=True)
            df = df.drop(index=i).reset_index(drop=True)

            save_data(df)
            st.success("Record deleted!")
            st.rerun()
    return df

# --- Edit record form ---
def edit_record(df, idx, current_user):
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

# def filter_data(df):
#     if "name" not in df.columns:
#         return df
#     names = df["name"].dropna().unique().tolist()
#     selected = st.selectbox("Filter by Team Member", ["All"] + sorted(names))
#     if selected != "All":
#         return df[df["name"] == selected]
#     return df

# def display_table(df):
#     if df.empty:
#         st.info("No records to display.")
#         return df

#     if "edit_row_index" not in st.session_state:
#         st.session_state.edit_row_index = None
#     if "delete_row_index" not in st.session_state:
#         st.session_state.delete_row_index = None

#     cols = st.columns([2, 2, 1.5, 1.5, 1.5, 2, 0.8, 0.8])
#     headers = ["Name", "Task", "Status", "Start Date", "ETA", "Remarks", "✏️", "🗑️"]
#     for col, header in zip(cols, headers):
#         col.markdown(f"**{header}**")

#     for i, row in df.iterrows():
#         row_cols = st.columns([2, 2, 1.5, 1.5, 1.5, 2, 0.8, 0.8])
#         row_cols[0].write(row["name"])
#         row_cols[1].write(row["task"])
#         row_cols[2].write(row["status"])
#         row_cols[3].write(row["start_date"])
#         row_cols[4].write(row["eta"])
#         row_cols[5].write(row["remarks"])

#         if row_cols[6].button("Edit", key=f"edit_{i}"):
#             st.session_state.edit_row_index = i

#         if row_cols[7].button("Delete", key=f"delete_{i}"):
#             st.session_state.delete_row_index = i

#     return df


def download_excel(df):
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