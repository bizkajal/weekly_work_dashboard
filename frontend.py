import streamlit as st
import pandas as pd
from data_managers import load_data, save_data
import plotly.express as px
import plotly.graph_objects as go

def submit_form(df, current_user):
    activity_categories = [
        "Client Project", "PoC (Internal)", "PoC (External)",
        "Pre Sales - Business Development", "Pre Sales - Technology Research",
        "Interviews", "SME - Incident Management", "Certifications", "Conducting Trainings", "Meetings"
    ]

    with st.form(key=f"weekly_update_form_{current_user}_{len(df)}"):
        task = st.text_area("Task")
        status = st.selectbox("Status", ["In Progress", "Completed", "Blocked"])
        start_date = st.date_input("Start Date")
        eta = st.date_input("ETA")
        remarks = st.text_area("Remarks")
        category = st.selectbox("Activity Category", activity_categories)
        hours_spent = st.number_input("Hours spent on this task (out of 8)", min_value=0.0, max_value=40.0, step=0.25)

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
                "weightage": int(weightage)  # Store as integer percentage
            }

            full_df = load_data()
            full_df = pd.concat([full_df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(full_df)

            st.success("Entry submitted successfully!")
            st.rerun()

    return df


def display_table(df, current_user):
    st.subheader("Team Status Overview")

    if df.empty:
        st.info("No records to display yet.")
        return df

    header_cols = st.columns([2, 2, 1.5, 1.5, 1.5, 2, 2, 1.5, 1.2, 1.2])
    headers = ["Name", "Task", "Status", "Start Date", "ETA", "Remarks", "Category", "Weightage %"]
    for col, header in zip(header_cols, headers):
        col.markdown(f"**{header}**")

    for i, row in df.iterrows():
        cols = st.columns([2, 2, 1.5, 1.5, 1.5, 2, 2, 1.5, 1.2, 1.2])
        cols[0].write(row["name"])
        cols[1].write(row["task"])
        cols[2].write(row["status"])
        cols[3].write(row["start_date"])
        cols[4].write(row["eta"])
        cols[5].write(row["remarks"])
        cols[6].write(row.get("category", ""))
        cols[7].write(f"{row.get('weightage', 0)}%")

        can_edit = (current_user == "admin") or (row["name"] == current_user)
        can_delete = can_edit

        if can_edit and cols[8].button("Edit", key=f"edit_{i}"):
            st.session_state.edit_row_index = i
            st.rerun()

        if can_delete and cols[9].button("Delete", key=f"delete_{i}"):
            df = df.drop(index=i).reset_index(drop=True)
            save_data(df)
            st.success("Record deleted!")
            st.rerun()

    return df

def edit_record(df, idx, current_user):
    st.subheader("Edit Record")
    row = df.loc[idx]

    with st.form("edit_form"):
        name = st.text_input("Name", value=row["name"], disabled=(current_user != "admin"))
        task = st.text_area("Task", value=row["task"])

        statuses = ["In Progress", "Completed", "Blocked"]
        status = st.selectbox("Status", statuses, index=statuses.index(row["status"]) if row["status"] in statuses else 0)

        start_date = st.date_input("Start Date", value=pd.to_datetime(row["start_date"]).date())
        eta = st.date_input("ETA", value=pd.to_datetime(row["eta"]).date())
        remarks = st.text_area("Remarks", value=row["remarks"])

        categories = [
            "Client Project", "PoC (Internal)", "PoC (External)",
            "Pre Sales - Business Development", "Pre Sales - Technology Research",
            "Interviews", "SME - Incident Management", "Certifications",
            "Conducting Trainings", "Meetings"
        ]
        category = st.selectbox("Activity Category", categories, index=categories.index(row.get("category", categories[0])))

        default_hours = round((row.get("weightage", 0) * 40) / 100, 2)
        hours_spent = st.number_input("Hours spent on this task (out of 40)", min_value=0.0, max_value=8.0, value=default_hours, step=0.25)

        submitted = st.form_submit_button("Update Record")

        if submitted:
            weightage = int((hours_spent / 40) * 100)

            df.at[idx, "name"] = name
            df.at[idx, "task"] = task
            df.at[idx, "category"] = category
            df.at[idx, "status"] = status
            df.at[idx, "weightage"] = weightage
            df.at[idx, "start_date"] = start_date.strftime("%Y-%m-%d")
            df.at[idx, "eta"] = eta.strftime("%Y-%m-%d")
            df.at[idx, "remarks"] = remarks

            save_data(df)
            st.success("Record updated!")
            st.session_state.edit_row_index = None
            st.rerun()
            

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


def show_donut_chart_plotly(df, selected_member, current_user):
    """
    Shows a Plotly donut chart for activity distribution.

    - If admin & selected_member == "All" → team-wide aggregate
    - Else → individual user chart
    """
    # st.subheader("Activity Distribution")

    if current_user == "admin" and selected_member == "All":
        if df.empty:
            st.info("No data available for team activity chart.")
            return
        agg_team = df.groupby("category")["weightage"].sum()
        labels = agg_team.index.tolist()
        values = agg_team.values.tolist()
        title = "Overall Team Activity Distribution"
    else:
        user_df = df[df["name"] == selected_member] if current_user == "admin" else df[df["name"] == current_user]
        if user_df.empty:
            st.info("No activity data to visualize.")
            return
        agg_user = user_df.groupby("category")["weightage"].sum()
        labels = agg_user.index.tolist()
        values = agg_user.values.tolist()
        title = f"Activity Distribution for {selected_member if current_user == 'admin' else current_user}"

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        hoverinfo='label+percent',
        textinfo='label+percent'
    )])
    fig.update_layout(title_text=title)
    st.plotly_chart(fig, use_container_width=True)
