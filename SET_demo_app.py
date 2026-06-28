import streamlit as st
import pandas as pd
from pathlib import Path

import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

import visuals_util as vis_util
import interactive_visuals as ivis

# Page configuration
st.set_page_config(
    page_title="Student Evaluation of Teaching Demo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.metric-container {
    background-color: #f0f2f6;
    border: 1px solid #d0d0d0;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
.sidebar-content {
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Navigation
pages = {
    "Cross-semester analytics": "cross_semester_vis",
    "Topic-focused analytics": "topic_category_vis",
    "Semester-focused analytics": "semester_vis",
    "Feedback summary": "summary"
}

# Sidebar navigation
st.sidebar.title("Student feedback analytics")
selected_page = st.sidebar.radio("Choose from the list below", list(pages.keys()))

# load the data
pos_comments = pd.read_csv(Path.cwd() / 'data' / 'positive_cross_category_cnts_for_visualisation.csv')
neg_comments = pd.read_csv(Path.cwd() / 'data' / 'negative_cross_category_cnts_for_visualisation.csv')
all_comments = pd.concat([pos_comments, neg_comments])
summaries = pd.read_csv(Path.cwd() / 'data' / 'all_summaries.csv')

# some auxiliary variables
min_year = all_comments['year'].min() #max(pos_comments.year.min(), neg_comments.year.min())
max_year = all_comments['year'].max() #min(pos_comments.year.max(), neg_comments.year.max())
year_range = range(min_year, max_year+1)
topical_categories = all_comments['category'].unique().tolist()

# Page content
if selected_page == "Cross-semester analytics":
    st.title("Cross-semester analytics of student feedback")

    col_cs1, col_cs2 = st.columns(2)
    start_year = col_cs1.select_slider('Start year', options=year_range, value=min_year)
    end_year = col_cs2.select_slider('End year', options=year_range, value=max_year)
    # start_year = st.selectbox('Start year', options=year_range, index=0)
    # end_year = st.selectbox('End year', options=year_range, index=len(year_range)-1)

    st.subheader("Distribution of positive comments across distinct course aspects")

    pos_comments_wide = vis_util.filter_and_transform_data_to_visualize(pos_comments, start_year, end_year)
    pos_plt = ivis.plot_cross_semester_topic_distribution_plotly(pos_comments_wide)
    st.plotly_chart(pos_plt)

    st.subheader("Distribution of negative comments across distinct course aspects")

    neg_comments_wide = vis_util.filter_and_transform_data_to_visualize(neg_comments, start_year, end_year)
    neg_plt = ivis.plot_cross_semester_topic_distribution_plotly(neg_comments_wide)
    st.plotly_chart(neg_plt)

elif selected_page == "Topic-focused analytics":
    st.title("Topic-focused sentiment across semesters")

    col_tf1, col_tf2, col_tf3 = st.columns([1,1,2])
    start_year_p2 = col_tf1.select_slider('Start year', options=year_range, value=min_year)
    end_year_p2 = col_tf2.select_slider('End year', options=year_range, value=max_year)
    topic = col_tf3.selectbox('Select topical category', options=topical_categories, index=0)

    topic_plt = ivis.plot_pos_vs_neg_props_for_topical_category_plotly(pos_comments,
                                                                       neg_comments,
                                                                       start_year_p2,
                                                                       end_year_p2,
                                                                       topic)
    st.plotly_chart(topic_plt)

elif selected_page == "Semester-focused analytics":
    st.title("Distribution of positive and negative comments in a semester")

    st.write('Choose the year and the semester to examine the feedback analytics')
    col_sf1, col_sf2 = st.columns([2,1])
    with col_sf1:
        # year = st.selectbox('Choose academic year', options=year_range, index=year_range.index(max_year))
        year_page3 = st.select_slider('Choose academic year', options=year_range, value=max_year)
    with col_sf2:
        semester_range = vis_util.get_semesters_for_year(all_comments, year_page3)
        semester_page3 = st.selectbox('Choose a semester within the chosen academic year',
                                options=semester_range, index=0)

    pos_vs_neg_plt = ivis.plot_pos_vs_neg_props_for_semester_plotly(pos_comments,
                                                                        neg_comments,
                                                                        f'{year_page3}{semester_page3}')
    st.plotly_chart(pos_vs_neg_plt)

elif selected_page == "Feedback summary":
    st.title("Summary of the feedback from a particular student cohort")

    st.write('Choose the year, semester, and study group to get a summary of the student feedback')
    col_sum1, col_sum2, col_sum3 = st.columns([2, 1, 1])
    with col_sum1:
        # year = st.selectbox('Choose academic year', options=range(2018, 2026), index=year_range.index(2025))
        year_page4 = st.select_slider('Choose academic year', options=year_range, value=max_year)
    with col_sum2:
        semester_range = vis_util.get_semesters_for_year(summaries, year_page4)
        if len(semester_range) > 0:
            semester_page4 = st.selectbox('Choose a semester within the academic year',
                                    options=semester_range)
        else:
            semester_page4 = None
            st.error("No data for the chosen period")
    with col_sum3:
        if semester_page4:
            chosen_semester_str = f'{year_page4}{semester_page4}'
            course_sections = summaries.loc[summaries.semester==int(chosen_semester_str)].section.unique().tolist()
            group = st.selectbox('Choose a study group to focus on', options=course_sections)
        else:
            st.error("No data for the chosen period")

    # vis_util.display_summary_matrix(summaries,
    #                                 chosen_semester=f'{year}{semester}',
    #                                 chosen_section=group)
    if semester_page4 and group:
        vis_util.display_summary_cards(summaries,
                                       chosen_semester=chosen_semester_str,
                                       chosen_section=group)
