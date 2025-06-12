import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from services.data_managers import load_data, save_data, DB_FILE


def submit_form(current_user):
    activity_categories = [
        "Client Project",
        "PoC (Internal)",
        "PoC (External)",
        "Pre Sales - Business Development",
        "Pre Sales - Technology Research",
        "Interviews",
        "SME - Incident Management",
        "Certifications",
        "Conducting Trainings",
        "Meetings",
    ]

    with st.form(key=f"weekly_update_form_{current_user}"):
        category = st.selectbox("Activity Category", activity_categories)
        start_date = st.date_input("Start Date")
        eta = st.date_input("ETA")
        task = st.text_area("Task")
        status = st.selectbox("Status", ["In Progress", "Completed", "Blocked"])
        hours_spent = st.number_input(
            "Hours spent on this task (out of 8)",
            min_value=0.0,
            max_value=40.0,
            step=0.25,
        )
        remarks = st.text_area("Remarks")
        submitted = st.form_submit_button("Submit")

        if submitted:
            weightage = (hours_spent / 40) * 100  # Calculate percentage automatically
            new_entry = {
                "name": current_user,
                "task": task,
                "status": status,
                "start_date": str(start_date),
                "eta": str(eta),
                "remarks": remarks,
                "category": category,
                "weightage": int(weightage),  # Store as integer percentage
            }

            full_df = load_data()
            full_df = pd.concat([full_df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(full_df)

            st.success("Entry submitted successfully!")
            st.rerun()

        return ""

def sync_changes_to_db(original_df: pd.DataFrame, edited_df: pd.DataFrame):
    index = "rowId"
    # set rowId column as an index to both the dataframe
    original_df.set_index(index, inplace=True)
    edited_df.set_index(index, inplace=True)

    # get user name to append to the database
    name = st.session_state.user
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            # get updates if made any new rows
            for id, edited_rows in edited_df.iterrows():
                if id in original_df.index:
                    original_row = original_df.loc[id]
                    # checks if any updates has happend
                    if not edited_rows.equals(original_row):
                        # do UPDATE on rows where edit has occured.
                        cursor.execute(
                            "UPDATE updates SET task=?, category=?, status=?, start_date=?, eta=?, remarks=? WHERE rowId=?",
                            (
                                edited_rows["task"],
                                edited_rows["category"],
                                edited_rows["status"],
                                edited_rows["start_date"],
                                edited_rows["eta"],
                                edited_rows["remarks"],
                                id,
                            ),
                        )
    except Exception as e:
        raise Exception("Error occured while trying to update records to the database.")

    return True

def create_editable_df():
    data_snapshot = st.session_state.user_activities
    # --- Editable Data Editor ---
    # only allow edits to existing rows (no add/delete)
    edited_data = st.data_editor(
        data_snapshot,
        num_rows="fixed",
        column_config={
            "rowId": st.column_config.Column("rowId", disabled=True),  # 🔒 read-only
            "name": st.column_config.Column("Name", disabled=True),
            "category": st.column_config.Column("Category"),
            "start_date": st.column_config.Column("Start Date"),
            "eta": st.column_config.Column("ETA"),
            "Task": st.column_config.Column("Task"),
            "status": st.column_config.Column("Status"),
            "weightage": st.column_config.Column("Weightage", disabled=True),
        },
        # use_container_width=True,
        key="editor",
    )

    # --- Save Changes Button ---
    if st.button("💾 Save Changes"):
        st.session_state.user_activities = edited_data
        # get the updated value, and where its changed, and update by its primary key
        if sync_changes_to_db(data_snapshot, edited_data):
            st.success("Changes saved!")
        else:
            st.error("Changes are not saved to the database!")
    
    st.session_state.user_activities = edited_data # update the user_activities across

def show_donut_chart_plotly(df, selected_member, current_user):
    """
    Shows a Plotly donut chart for activity distribution.

    - If admin & selected_member == "All" → team-wide aggregate
    - Else → individual user chart
    """
    st.header("Overall Distribution")

    print("Current User:{}, Selected Member:{}".format(current_user, selected_member))

    if current_user == "admin" and selected_member == "All":
        if df.empty:
            st.info("No data available for team activity chart.")
            return
        agg_team = df.groupby("category")["weightage"].sum()
        labels = agg_team.index.tolist()
        values = agg_team.values.tolist()
        title = "Overall Team Activity Distribution"
    else:
        user_df = (
            df[df["name"] == selected_member]
            if current_user == "admin"
            else df[df["name"] == current_user]
        )
        if user_df.empty:
            st.info("No activity data to visualize.")
            return
        agg_user = user_df.groupby("category")["weightage"].sum()
        labels = agg_user.index.tolist()
        values = agg_user.values.tolist()
        title = f"Activity Distribution for {selected_member if current_user == 'admin' else current_user}"

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                hoverinfo="label+percent",
                textinfo="label+percent",
            )
        ]
    )
    fig.update_layout(title_text=title)
    st.plotly_chart(fig, use_container_width=True)

def show_plot_graph(df, selected_member, current_user):
    if current_user == "admin":
        # <!--- Some filter will apply here --->
        pass

    st.header(" # by Status")
    # get status count
    status_count = df["status"].value_counts().reset_index()
    status_count.columns = ["status", "counts"]
    print("Status count Dataframe:{}".format(status_count))
    # Plot using Plotly
    fig = px.bar(
        status_count,
        x="status",
        y="counts",
        title="Task Count by Status",
        color="status",
        text="counts"
    )

    # Display in Streamlit
    st.plotly_chart(fig)

