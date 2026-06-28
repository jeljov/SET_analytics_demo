import matplotlib.pyplot as plt
import seaborn as sb
import pandas as pd
import numpy as np
import streamlit as st

def get_semesters_for_year(comments_df: pd.DataFrame, year:int):
    df = comments_df[['year', 'semester']]
    df.drop_duplicates(inplace=True)
    semesters = df.loc[df.year==year]['semester'].tolist()
    # semesters are stored as int values in the form <year><semester_number>, so get just the <semester_number>
    return [semester % 10 for semester in semesters] if semesters else []

def filter_and_transform_data_to_visualize(comments_cnts_df, start_year, end_year):
    df = comments_cnts_df.loc[(comments_cnts_df.year >= start_year) & (comments_cnts_df.year <= end_year)]
    # df.semester = df.semester.astype('str')
    df_wide = df.pivot(index='semester', columns='category', values='comments_prop')
    df_wide.fillna(value=0, inplace=True)
    if 'Other' in df_wide.columns.tolist():
        df_wide.drop(columns='Other', inplace=True)
    return df_wide


def filter_and_transform_summaries_data(summaries_df:pd.DataFrame,
                                        chosen_semester:str,
                                        chosen_section: str):

    filtered_df = summaries_df[
        (summaries_df['semester'] == int(chosen_semester)) &
        (summaries_df['section'] == chosen_section)
        ]

    if filtered_df.empty:
        raise RuntimeError("No data available for the selected semester and section.")

    # pivot to get categories as rows and sentiments as columns
    try:
        matrix_df = filtered_df.pivot(
            index='category',
            columns='sentiment',
            values='summary'
        )

        # Ensure both columns exist even if one sentiment is missing in the data
        for sent in ['positive', 'negative']:
            if sent not in matrix_df.columns:
                matrix_df[sent] = "No summaries available."

        # Reorder columns explicitly to keep positive on the left, negative on the right
        available_cols = [col for col in ['positive', 'negative'] if col in matrix_df.columns]
        matrix_df = matrix_df[available_cols]

        # Fill any individual NaN cells where a category only had one sentiment type
        matrix_df = matrix_df.fillna("No summary available for this category.")

        return matrix_df

    except ValueError:
        raise RuntimeError("Data duplication error: Ensure there is only one summary per category/sentiment combination.")

    return None


def display_summary_matrix(summaries_df, chosen_semester: str, chosen_section: str):
    st.subheader(f"Feedback Summaries for {chosen_section} ({chosen_semester})")

    # Filter the dataset based on selections
    try:
        matrix_df = filter_and_transform_summaries_data(summaries_df, chosen_semester, chosen_section)
    except RuntimeError as e:
        st.error(str(e))
        return

    # Display Options in Streamlit
    st.dataframe(
        matrix_df,
        width='stretch',
        column_config={
            "category": st.column_config.TextColumn("Course Aspect", width="medium"),
            "positive": st.column_config.TextColumn("🟢 Positive Summary", width="large"),
            "negative": st.column_config.TextColumn("🔴 Negative Summary", width="large"),
        }
    )


def display_summary_cards(summaries_df, chosen_semester: str, chosen_section: str):
    # Filter data
    filtered_df = summaries_df[
        (summaries_df['semester'] == int(chosen_semester)) &
        (summaries_df['section'] == chosen_section)
        ]

    if filtered_df.empty:
        st.error("No data available for the selected semester and section.")

    # Get a unique, sorted list of categories present
    categories = sorted(filtered_df['category'].unique())

    st.write("---")

    # Iterate through categories row-by-row
    for category in categories:
        # Wrap everything for this specific category in a container block
        with st.container():
            st.markdown(f"#### 🏷️ {category}")

            # Create two equal columns for the split presentation
            col_pos, col_neg = st.columns(2)

            # Extract specific summaries
            pos_text = \
            filtered_df[(filtered_df['category'] == category) &
                        (filtered_df['sentiment'].str.lower() == 'positive')]['summary'].values
            neg_text = \
            filtered_df[(filtered_df['category'] == category) &
                        (filtered_df['sentiment'].str.lower() == 'negative')]['summary'].values

            # Fallback texts if one sentiment side is completely empty
            has_pos_summary = len(pos_text) > 0
            has_neg_summary = len(neg_text) > 0
            pos_summary = pos_text[0] if has_pos_summary else "No positive remarks recorded for this aspect."
            neg_summary = neg_text[0] if has_neg_summary else "No critical remarks or improvements recorded for this aspect."


            # Left Column: Positive Feedback Card
            with col_pos:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #f0fdf4; 
                        border-left: 5px solid #16a34a; 
                        padding: 15px; 
                        border-radius: 4px;
                        height: 100%;
                    ">
                        <strong style="color: #15803d;">🟢 Positive Highlights</strong><br>
                        <p style="color: #1f2937; margin-top: 8px; font-size: 16px; line-height: 1.5;">
                            {pos_summary}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Right Column: Negative Feedback Card
            with col_neg:
                if has_neg_summary:
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #fef2f2; 
                            border-left: 5px solid #dc2626; 
                            padding: 15px; 
                            border-radius: 4px;
                            height: 100%;
                        ">
                            <strong style="color: #b91c1c;">🔴 Areas for Improvement</strong><br>
                            <p style="color: #1f2937; margin-top: 8px; font-size: 16px; line-height: 1.5;">
                                {neg_summary}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #cdf8fa; 
                            border-left: 5px solid #22a4ab; 
                            padding: 15px; 
                            border-radius: 4px;
                            height: 100%;
                        ">
                            <p style="color: #1f2937; margin-top: 4px; font-size: 16px; line-height: 1.5;">
                                {neg_summary}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # Add subtle spacing before the next course aspect row
            st.write("")
            st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)


def plot_cross_semester_topic_distribution(comments_to_plot, show_legend=True):
    sb.set_theme(style="white")  # Clean background
    plt.rcParams["font.family"] = "sans-serif"  # Clean font
    plt.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "DejaVu Sans"]

    # Use a cohesive, distinct 8-color palette (Muted/Pro look)
    categories = comments_to_plot.columns.tolist()
    colors = sb.color_palette("Paired", len(categories))

    fig, ax = plt.subplots(figsize=(11, 9))

    # Plot the stacked bars
    left_margin = np.zeros(len(comments_to_plot))  # Tracks the bottom/left start point of each segment

    categories_to_plot = comments_to_plot.columns.tolist()
    for i, category in enumerate(categories_to_plot):
        ax.barh(
            [str(i) for i in comments_to_plot.index],
            comments_to_plot[category],
            left=left_margin,
            label=category,
            color=colors[i],
            edgecolor="white",
            height=0.6,  # Sleeker bar width
        )
        left_margin += comments_to_plot[category]

    # Refine Aesthetics & Formatting
    ax.set_xlabel("Proportion of Total Comments", fontsize=12, labelpad=10)

    # Format X-axis to show percentages beautifully
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter("{x:.2f}")  # "{x:,.0f}%")

    # Clean up spines (borders) for a modern flat design
    sb.despine(left=True, bottom=True)

    # Add faint vertical gridlines to help guide the eye without cluttering
    ax.grid(axis="x", linestyle="--", alpha=0.5, color="#cccccc")

    # Position the legend neatly outside the plot on the right
    if show_legend:
        ax.legend(
            title="Comment Categories",
            title_fontsize="11",
            fontsize="10",
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
            frameon=False,  # Removes the box outline around legend
        )

    plt.tight_layout()

    return fig


def plot_pos_vs_neg_props_for_semester(pos_comment_cnts_df, neg_comment_cnts_df, semester:str):
    pos_df_sub = pos_comment_cnts_df.loc[(pos_comment_cnts_df.category != 'Other') &
                                          (pos_comment_cnts_df.semester == int(semester)),['category', 'comments_prop']]
    neg_df_sub = neg_comment_cnts_df.loc[(neg_comment_cnts_df.category != 'Other') &
                                          (neg_comment_cnts_df.semester == int(semester)), ['category', 'comments_prop']]

    df_sub = pd.merge(pos_df_sub, neg_df_sub, on='category', how='outer')
    df_sub.columns = ['category', 'pos_prop', 'neg_prop']
    df_sub.sort_values(by='category', inplace=True)
    df_sub.fillna(0, inplace=True)
    # print(df_sub.head(10))

    categories = df_sub.category
    pos_props = df_sub.pos_prop
    neg_props = -df_sub.neg_prop

    fig, ax = plt.subplots(figsize=(9,7))
    # Use negative values for the left side
    ax.barh(categories, neg_props, color='#ff7f0e', label='Negative comments')
    ax.barh(categories, pos_props, color='#1f77b4', label='Positive comments')

    # Remove Top and Right boundaries (spines)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 2. Position the Legend (Top Right, outside plot area)
    ax.legend(loc='upper right', bbox_to_anchor=(1, 1.1), ncol=2, frameon=False)

    # 3. Clean up the X-axis (Absolute values instead of negatives)
    max_val = max(df_sub.pos_prop.max(), df_sub.neg_prop.max())
    ticks = np.linspace(-max_val, max_val, 7)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{abs(x):.2f}" for x in ticks])

    # Optional: Add a central vertical line for better symmetry
    ax.axvline(0, color='black', linewidth=0.8, alpha=0.7)

    plt.tight_layout()

    return fig