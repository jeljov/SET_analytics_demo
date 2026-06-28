import numpy as np
import pandas as pd
import plotly.graph_objects as go
import seaborn as sb
import streamlit as st


def pprint_semester(semester: int):
    year, smstr = divmod(semester, 10)
    return f'{year} / {smstr}'

def plot_cross_semester_topic_distribution_plotly(comments_to_plot, show_legend=True):
    categories = comments_to_plot.columns.tolist()

    # Grab the "Paired" palette from seaborn and convert to hex strings for Plotly
    sb_colors = sb.color_palette("Paired", len(categories))
    colors = [
        f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"
        for r, g, b in sb_colors
    ]

    fig = go.Figure()

    # Reconstruct the stacked horizontal bars
    # Convert index to string to match your categorical y-axis behavior
    y_labels = [pprint_semester(idx) for idx in comments_to_plot.index]

    for i, category in enumerate(categories):
        fig.add_trace(
            go.Bar(
                name=category,
                y=y_labels,
                x=comments_to_plot[category],
                orientation="h",
                marker=dict(
                    color=colors[i],
                    line=dict(
                        color="white", width=1.5
                    ),  # White gap between segments
                ),
                width=0.6,  # Sleeker bar width (same as height=0.6 in matplotlib)
                # Custom interactive tooltip formatting
                hovertemplate=f"<b>{category}</b><br>Semester: %{{y}}<br>Proportion: %{{x:.2f}}<extra></extra>",
            )
        )

    # Apply custom styling and layout constraints to match your design
    fig.update_layout(
        barmode="stack",
        # Match your figure aspect ratio/dimensions
        width=1100,
        height=900,
        paper_bgcolor="white",
        plot_bgcolor="white",
        # Custom Font family configuration
        font=dict(
            family="Helvetica, Arial, DejaVu Sans, sans-serif", size=12
        ),
        # Configure X-Axis (Formatting, limits, grids)
        xaxis=dict(
            title="Proportion of Total Comments",
            title_font=dict(size=12),
            range=[0, 1],
            tickformat=".2f",  # Matches your "{x:.2f}" formatter
            showgrid=True,
            gridcolor="#cccccc",
            gridwidth=1,
            griddash="dash",  # Faint vertical dashed gridlines
            zeroline=False,
            showline=False,
        ),
        # Configure Y-Axis (Clean style, removes vertical lines)
        yaxis=dict(
            autorange="reversed",  # Keeps the first index at the top, matching matplotlib behavior
            showgrid=False,
            zeroline=False,
            showline=False,
            type="category",
        ),
        # Position the legend neatly outside the plot on the right
        showlegend=show_legend,
        legend=dict(
            title=dict(text="Comment Categories", font=dict(size=14)),
            font=dict(size=14),
            orientation="v",
            x=1.02,
            y=1,
            xanchor="left",
            yanchor="top",
        ),
        margin=dict(
            l=50, r=50, t=50, b=50
        ),  # Mimics plt.tight_layout padding
    )

    return fig


def plot_pos_vs_neg_props_for_semester_plotly(pos_comment_cnts_df: pd.DataFrame,
                                              neg_comment_cnts_df: pd.DataFrame,
                                              semester: str):
    # --- Data Wrangling (Kept exactly identical to your logic) ---
    pos_df_sub = pos_comment_cnts_df.loc[
        (pos_comment_cnts_df.category != "Other")
        & (pos_comment_cnts_df.semester == int(semester)),
        ["category", "comments_prop"],
    ]
    neg_df_sub = neg_comment_cnts_df.loc[
        (neg_comment_cnts_df.category != "Other")
        & (neg_comment_cnts_df.semester == int(semester)),
        ["category", "comments_prop"],
    ]

    if len(pos_df_sub) == 0 and len(neg_df_sub) == 0:
        st.error("No data available for the selected semester")
        return

    df_sub = pd.merge(pos_df_sub, neg_df_sub, on="category", how="outer")
    df_sub.columns = ["category", "pos_prop", "neg_prop"]
    df_sub.sort_values(by="category", inplace=True)
    df_sub.fillna(0, inplace=True)

    categories = df_sub.category.tolist()
    pos_props = df_sub.pos_prop.tolist()
    # Keep negative for positioning, but we'll prettify the tooltips
    neg_props = (-df_sub.neg_prop).tolist()

    # --- Plotly Figure Construction ---
    fig = go.Figure()

    # Left Side: Negative Comments
    fig.add_trace(
        go.Bar(
            y=categories,
            x=neg_props,
            name="Negative comments",
            orientation="h",
            marker=dict(color="#ff7f0e"),
            # Tooltip: display absolute value dynamically using df_sub.neg_prop
            hovertemplate="<b>%{y}</b><br>Negative: %{customdata:.2f}<extra></extra>",
            customdata=df_sub.neg_prop,
        )
    )

    # Right Side: Positive Comments
    fig.add_trace(
        go.Bar(
            y=categories,
            x=pos_props,
            name="Positive comments",
            orientation="h",
            marker=dict(color="#1f77b4"),
            hovertemplate="<b>%{y}</b><br>Positive: %{x:.2f}<extra></extra>",
        )
    )

    # Calculate max absolute value to ensure perfectly symmetrical X-axis bounds
    max_val = max(df_sub.pos_prop.max(), df_sub.neg_prop.max())
    # Add a 5-10% padding buffer so bars don't touch the very edges of the plot
    axis_limit = max_val * 1.1

    # --- Explicitly generate symmetrical tick marks ---
    # Create 7 evenly spaced tick locations between -max_val and +max_val
    raw_ticks = np.linspace(-max_val, max_val, 7)

    # Map those locations to their string representations using absolute values
    absolute_tick_labels = [f"{abs(x):.2f}" for x in raw_ticks]

    # --- Layout & Aesthetic Refinements ---
    fig.update_layout(
        barmode="overlay",  # Overlay works perfectly since one side is purely negative
        width=900,
        height=700,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Helvetica, Arial, DejaVu Sans, sans-serif", size=12),
        # X-Axis Styling
        xaxis=dict(
            title="Proportion of All Positive / Negative Comments in the Given Semester",
            range=[-axis_limit, axis_limit],

            # FORCE ABSOLUTE LABELS HERE:
            tickmode="array",
            tickvals=list(raw_ticks),
            ticktext=absolute_tick_labels,

            zeroline=True,
            zerolinecolor="black",  # Replaces ax.axvline(0)
            zerolinewidth=1,
            showgrid=False,
            showline=False,
        ),
        # Y-Axis Styling
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            type="category",
            tickfont=dict(size=14)
        ),
        # Legend Positioned at the top center/right, matching your setup
        showlegend=True,
        legend=dict(
            orientation="h",
            x=1.0,
            y=1.1,
            xanchor="right",
            yanchor="bottom",
            font=dict(size=14)
        ),
        margin=dict(l=50, r=50, t=80, b=50),
    )

    return fig


def plot_pos_vs_neg_props_for_topical_category_plotly(pos_comment_cnts_df: pd.DataFrame,
                                                      neg_comment_cnts_df: pd.DataFrame,
                                                      start_year: int,
                                                      end_year: int,
                                                      category: str):
    # --- Data Wrangling (Kept exactly identical to your logic) ---
    pos_df_sub = pos_comment_cnts_df.loc[
        (pos_comment_cnts_df.category == category)
        & (pos_comment_cnts_df.year >= start_year)
        & (pos_comment_cnts_df.year <= end_year),
        ["semester", "comments_prop"],
    ]
    neg_df_sub = neg_comment_cnts_df.loc[
        (neg_comment_cnts_df.category == category)
        & (neg_comment_cnts_df.year >= start_year)
        & (neg_comment_cnts_df.year <= end_year),
        ["semester", "comments_prop"],
    ]

    if len(pos_df_sub) == 0 and len(neg_df_sub) == 0:
        st.error("No data available for the selected period and course aspect")
        return

    df_sub = pd.merge(pos_df_sub, neg_df_sub, on="semester", how="outer")
    df_sub.columns = ["semester", "pos_prop", "neg_prop"]
    df_sub.sort_values(by="semester", inplace=True)
    df_sub.fillna(0, inplace=True)

    semesters = [pprint_semester(sem) for sem in df_sub.semester.tolist()]
    pos_props = df_sub.pos_prop.tolist()
    # Keep negative for positioning, but we'll prettify the tooltips
    neg_props = (-df_sub.neg_prop).tolist()

    # --- Plotly Figure Construction ---
    fig = go.Figure()

    # Left Side: Negative Comments
    fig.add_trace(
        go.Bar(
            y=semesters,
            x=neg_props,
            name="Negative comments",
            orientation="h",
            marker=dict(color="#ff7f0e"),
            # Tooltip: display absolute value dynamically using df_sub.neg_prop
            hovertemplate="<b>Semester %{y}</b><br>Negative: %{customdata:.2f}<extra></extra>",
            customdata=df_sub.neg_prop,
        )
    )

    # Right Side: Positive Comments
    fig.add_trace(
        go.Bar(
            y=semesters,
            x=pos_props,
            name="Positive comments",
            orientation="h",
            marker=dict(color="#1f77b4"),
            hovertemplate="<b>Semester %{y}</b><br>Positive: %{x:.2f}<extra></extra>",
        )
    )

    # Calculate max absolute value to ensure perfectly symmetrical X-axis bounds
    max_val = max(df_sub.pos_prop.max(), df_sub.neg_prop.max())
    # Add a 5-10% padding buffer so bars don't touch the very edges of the plot
    axis_limit = max_val * 1.1

    # --- Explicitly generate symmetrical tick marks ---
    # Create 7 evenly spaced tick locations between -max_val and +max_val
    raw_ticks = np.linspace(-max_val, max_val, 7)

    # Map those locations to their string representations using absolute values
    absolute_tick_labels = [f"{abs(x):.2f}" for x in raw_ticks]

    # --- Layout & Aesthetic Refinements ---
    fig.update_layout(
        barmode="overlay",  # Overlay works perfectly since one side is purely negative
        width=900,
        height=700,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Helvetica, Arial, DejaVu Sans, sans-serif", size=12),
        # X-Axis Styling
        xaxis=dict(
            title="Proportion of All Positive / Negative Comments on the Chosen Course Aspect",
            range=[-axis_limit, axis_limit],

            # FORCE ABSOLUTE LABELS HERE:
            tickmode="array",
            tickvals=list(raw_ticks),
            ticktext=absolute_tick_labels,

            zeroline=True,
            zerolinecolor="black",  # Replaces ax.axvline(0)
            zerolinewidth=1,
            showgrid=False,
            showline=False,
        ),
        # Y-Axis Styling
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            type="category",
            tickfont=dict(size=14)
        ),
        # Legend Positioned at the top center/right, matching your setup
        showlegend=True,
        legend=dict(
            orientation="h",
            x=1.0,
            y=1.1,
            xanchor="right",
            yanchor="bottom",
            font=dict(size=14)
        ),
        margin=dict(l=50, r=50, t=80, b=50),
    )

    return fig