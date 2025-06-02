import streamlit as st
import pandas as pd
from datetime import date
import io

def submit_form(df):
    with st.form("status_form"):
        st.subheader("🔄 Submit Your Weekly Update")
        name = st.text_input("Name")
        task = st.text_area("Task Description")
        status = st.selectbox("Status", ["In Progress", "Completed", "Blocked"])

        start_date = st.date_input("Start Date", value=date.today())
        eta = st.date_input("ETA", value=date.today())
        remarks = st.text_area("Remarks")
        submitted = st.form_submit_button("Submit Update")

        if submitted:
            if not name.strip():
                st.error("Please enter your name.")
                return df, False
            if not task.strip():
                st.error("Please describe your task.")
                return df, False

            # Use consistent column names and order (match your database schema)
            new_row = pd.DataFrame([{
                "Name": name,
                "Task": task,
                "Status": status,
                "start_date": str(start_date),
                "ETA": str(eta),
                "Remarks": remarks
            }])

            # If the existing df is empty, create columns
            if df.empty:
                df = new_row
            else:
                # Ensure columns match and order is correct
                df = pd.concat([df, new_row], ignore_index=True)
                df = df[["Name", "Task", "Status", "start_date", "ETA", "Remarks"]]  # Adjust if needed

            st.success("✅ Update submitted successfully!")
            return df, True

    return df, False

def filter_data(df):
    filter_name = st.selectbox("Filter by Team Member", ["All"] + sorted(df["Name"].unique().tolist()))
    if filter_name == "All":
        return df
    else:
        return df[df["Name"] == filter_name]

def display_table(df):
    st.dataframe(df, use_container_width=True)



def delete_records(df):
    st.subheader("🗑️ Manage Deletions") 

    # Main toggle to show delete section
    if "show_delete_main" not in st.session_state:
        st.session_state.show_delete_main = False
    if "show_delete_name" not in st.session_state:
        st.session_state.show_delete_name = False
    if "show_delete_records" not in st.session_state:
        st.session_state.show_delete_records = False

    # Toggle main delete panel
    if not st.session_state.show_delete_main:
        if st.button("🗑️ Show Delete Options"):
            st.session_state.show_delete_main = True
    else:
        if st.button("❌ Hide Delete Options"):
            st.session_state.show_delete_main = False
            st.session_state.show_delete_name = False
            st.session_state.show_delete_records = False

    # Nested toggles inside main panel
    if st.session_state.show_delete_main:
        st.markdown("### 🔧 Choose Deletion Method")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("👤 Delete by Team Member"):
                st.session_state.show_delete_name = not st.session_state.show_delete_name
        with col2:
            if st.button("🧾 Delete Specific Records"):
                st.session_state.show_delete_records = not st.session_state.show_delete_records

        # -- Delete by Name --
        if st.session_state.show_delete_name:
            st.markdown("#### 🔍 Delete All Records by Team Member")
            unique_names = sorted(df["Name"].unique().tolist())
            selected_name = st.selectbox("Select team member", ["None"] + unique_names, key="delete_by_name")

            if selected_name != "None":
                if st.button(f"Delete all records for {selected_name}", key="confirm_delete_name"):
                    df = df[df["Name"] != selected_name].reset_index(drop=True)
                    st.success(f"All records for '{selected_name}' have been deleted.")

        # -- Delete Specific Records --
        if st.session_state.show_delete_records:
            st.markdown("#### 🧾 Delete Specific Records")
            options = df.apply(lambda row: f"{row['Name']} - {row['Task']} (Started: {row['Start Date']})", axis=1).tolist()
            to_delete = st.multiselect("Select records to delete", options, key="delete_multiselect")

            if st.button("Delete Selected Records", key="confirm_delete_records"):
                if not to_delete:
                    st.warning("Please select at least one record to delete.")
                else:
                    indexes_to_delete = [options.index(rec) for rec in to_delete]
                    df = df.drop(df.index[indexes_to_delete]).reset_index(drop=True)
                    st.success(f"Deleted {len(to_delete)} record(s).")

    return df


def edit_records(df):
    st.subheader("✏️ Edit Records")

    if df.empty:
        st.info("No records available to edit.")
        return df

    options = df.apply(lambda row: f"{row['Name']} - {row['Task']} (Started: {row['Start Date']})", axis=1).tolist()
    selected = st.selectbox("Select a record to edit", ["None"] + options)

    if selected != "None":
        index = options.index(selected)
        row = df.loc[index]

        with st.form("edit_form"):
            st.markdown("### Update Details")
            name = st.text_input("Name", value=row["Name"])
            task = st.text_area("Task Description", value=row["Task"])
            status = st.selectbox("Status", ["In Progress", "Completed", "Blocked"],
                                  index=["In Progress", "Completed", "Blocked"].index(row["Status"]))
            start_date = st.date_input("Start Date", value=pd.to_datetime(row["Start Date"]).date())
            eta = st.date_input("ETA", value=pd.to_datetime(row["ETA"]).date())
            remarks = st.text_area("Remarks / Highlights", value=row["Remarks"] if pd.notnull(row["Remarks"]) else "")
            submitted = st.form_submit_button("Update Record")

            if submitted:
                df.loc[index] = [name, task, status, start_date, eta, remarks]
                st.success("✅ Record updated successfully!")

    return df

def download_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Status')
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Download as Excel",
        data=excel_data,
        file_name="team_status.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    