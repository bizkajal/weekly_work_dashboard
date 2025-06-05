import pandas as pd
import altair as alt
import streamlit as st

def calculate_weekly_occupancy(df, date_col='Start Date'):
    df[date_col] = pd.to_datetime(df[date_col])
    """Calculate weekly task hours and project occupancy percentage per team member."""
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['week'] = df['date'].dt.strftime('%Y-%U')

    # Identify task hour columns dynamically
    task_columns = [col for col in df.columns if col.endswith('_hours')]
    if not task_columns:
        st.warning("No task hour columns found in data.")
        return pd.DataFrame()

    weekly = df.groupby(['name', 'week'])[task_columns].sum().reset_index()
    weekly['Total_Hours'] = weekly[task_columns].sum(axis=1)

    if 'project_hours' in weekly.columns:
        weekly['Project_Occupancy_%'] = (weekly['project_hours'] / weekly['Total_Hours']) * 100
    else:
        weekly['Project_Occupancy_%'] = 0

    return weekly

def display_occupancy_bar_chart(weekly_df):
    """Display stacked bar chart of task time proportions per week and team member."""
    if weekly_df.empty:
        st.info("No data to show in the occupancy bar chart.")
        return

    task_columns = [col for col in weekly_df.columns if col.endswith('_hours')]
    df_melted = weekly_df.melt(id_vars=["name", "week"], value_vars=task_columns,
                               var_name="Task Category", value_name="Hours")

    chart = alt.Chart(df_melted).mark_bar().encode(
        x=alt.X('week:N', title='Week'),
        y=alt.Y('Hours:Q', stack='normalize', title="Proportion of Time"),
        color=alt.Color('Task Category:N', title="Task Category"),
        column=alt.Column('name:N', title="Team Member")
    ).properties(
        width=150,
        height=300
    ).configure_axis(
        labelAngle=0
    )

    st.altair_chart(chart, use_container_width=True)

def display_occupancy_heatmap(weekly_df):
    """Display heatmap of project occupancy percentage per team member per week."""
    if weekly_df.empty:
        st.info("No data to show in the occupancy heatmap.")
        return

    heatmap_data = weekly_df[["name", "week", "Project_Occupancy_%"]]

    chart = alt.Chart(heatmap_data).mark_rect().encode(
        x=alt.X('week:N', title="Week"),
        y=alt.Y('name:N', title="Team Member"),
        color=alt.Color('Project_Occupancy_%:Q', scale=alt.Scale(scheme='blues'), title="Project Occupancy %"),
        tooltip=['name', 'week', alt.Tooltip('Project_Occupancy_%:Q', format='.1f')]
    ).properties(
        width=600,
        height=400
    )

    st.altair_chart(chart, use_container_width=True)
