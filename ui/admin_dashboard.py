import streamlit as st
import pandas as pd
from ui.logout import render_logout
from services.data_managers import run_sqlite_query
from services.users_dashboard import (
    show_donut_chart_plotly,
    show_plot_graph,
)

def download_report(df):
    import io

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    st.download_button(
        label="Export CSV",
        data=processed_data,
        file_name="weekly_team_status.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

def render_admin_dashboard():
    col1, col2 = st.columns([8, 2])  # relative ratios

    # fetch full data from the updates database;
    full_data_query = "SELECT * FROM updates;"
    full_updates_data = run_sqlite_query(full_data_query)

    # layout 1 ---> welcome & logout
    with col1:
        st.title(f"Welcome, {st.session_state.user}!")
    with col2:
        render_logout()
    
    st.title("Activity Status")
    filter_col1, _ = st.columns([5,5])
    team_members = full_updates_data["name"].dropna().unique().tolist()
    with filter_col1:
        selected_member =  st.selectbox(
            "Filter By Team Member",
            ["All"] + sorted(team_members),
            key="filter_by_team_member"
        )
    
    if selected_member != "All":
        filtered_df = full_updates_data[full_updates_data["name"] == selected_member]
    else:
        filtered_df = full_updates_data.copy() # copy the entire dataframe
    
    dashboard_col1, dashboard_col2 = st.columns([5,5])
    print("Filtered dataframe shape:{}".format(filtered_df.shape))
    with dashboard_col1:
        show_donut_chart_plotly(
            filtered_df,
            selected_member=selected_member,
            current_user="admin"
        )
    
    with dashboard_col2:
        show_plot_graph(
            filtered_df,
            selected_member=selected_member,
            current_user=st.session_state.user
        )
    
    # filter by status Layout
    status_list = filtered_df["status"].dropna().unique().tolist()
    status_selected =  st.selectbox(
        "Filter By status",
        ["All"] + sorted(status_list),
        key="filter_by_status"
    )
    # use case 1: all & all
    if selected_member == "All" and status_selected == "All":
        status_query = f"SELECT * FROM updates;"
    # use case 2: all & status selected
    elif selected_member == "All" and status_selected:
        status_query = f"SELECT * from updates where status='{status_selected}'"
    # use case 3: user selected * all status
    elif selected_member != "All" and status_selected == "All":
        status_query = f"SELECT * FROM updates where name='{selected_member}'"
    # use case 4: user selected * status selected
    else:
        status_query = f"SELECT * FROM updates where name='{selected_member}' AND status='{status_selected}'"
    status_df = run_sqlite_query(status_query)
    st.dataframe(status_df, use_container_width=True)

    # download layout
    download_layout1, download_layout2 = st.columns([9, 1])
    with download_layout2:
        download_report(status_df)