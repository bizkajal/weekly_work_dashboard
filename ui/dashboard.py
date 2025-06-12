import streamlit as st
import pandas as pd
from ui.logout import render_logout
from services.users_dashboard import (
    submit_form,
    create_editable_df,
    show_donut_chart_plotly,
    show_plot_graph,
)
from services.data_managers import run_sqlite_query


def render_dashboard():
    col1, col2 = st.columns([8, 2])  # relative ratios
    # get required datafrom the table
    full_data_fetch = "SELECT rowId, name, category, start_date, eta, task, status, remarks, weightage FROM updates WHERE name='{}'".format(
        st.session_state.user
    )
    # execute the query
    full_user_data = run_sqlite_query(full_data_fetch)
    print("Dataframe shape:{}".format(full_user_data.shape))

    # set this dataframe through the user
    st.session_state.user_activities = full_user_data

    # layout 1 ---> welcome & logout
    with col1:
        st.title(f"Welcome, {st.session_state.user}!")
    with col2:
        render_logout()

    # layout 2 -----> dashboard & editable forms
    tabs = st.tabs(["Dashboard", "Fill Task"])
    # dashboard tab
    with tabs[0]:
        dashboard_col1, dashboard_col2 = st.columns([5,5])
        if full_user_data.shape[0] == 0:
            st.text("No records are found as per our database...")
        else:
            # layout 1 ---> For donut chart
            with dashboard_col1:
                selected_member = st.session_state.user
                current_user = st.session_state.user
                # show donut chart
                show_donut_chart_plotly(
                    st.session_state.user_activities, selected_member, current_user
                )
            # layout 2 ---> For bar graph to give overview # of items by Status
            with dashboard_col2:
                show_plot_graph(
                    st.session_state.user_activities, 
                    selected_member, 
                    current_user
                )
            # render the table
            # st.dataframe(full_user_data)
            st.header("Activity List")
            create_editable_df()

    with tabs[1]:
        submit_form(st.session_state.user)
