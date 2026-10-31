
import streamlit as st
import pandas as pd
import plotly.express as px

from labeler import label_comment
from storage import save_feedback, load_feedback


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="StayWise Hotel",
    page_icon="🏨",
    layout="wide"
)

st.title("🏨 StayWise Hotel")
st.subheader("Guest Feedback Analyzer")

st.write(
    "Welcome to StayWise Hotel! Share your experience "
    "and help us improve our services."
)

st.divider()


# --------------------------------------------------
# APPLICATION TABS
# --------------------------------------------------

tab_customer, tab_owner = st.tabs([
    "📝 Guest Feedback",
    "📊 Hotel Management Dashboard"
])


# --------------------------------------------------
# TAB 1: CUSTOMER FEEDBACK
# --------------------------------------------------

with tab_customer:

    st.header("Share Your Experience")

    st.write(
        "Tell us about your stay at StayWise Hotel. "
        "You can leave a comment, a star rating, or both."
    )

    with st.form("feedback_form"):

        guest_comment = st.text_area(
            "How was your stay?",
            placeholder="Tell us about your experience..."
        )

        guest_rating = st.feedback("stars")

        submit = st.form_submit_button("Submit Feedback")

    if submit:

        if not guest_comment.strip() and guest_rating is None:

            st.warning(
                "Please provide a comment, a star rating, or both."
            )

        else:

            if guest_comment.strip():

                with st.spinner("Analyzing your feedback..."):
                    try:
                        category = label_comment(
                            guest_comment.strip()
                        )
                    except Exception:
                        st.error(
                            "We couldn't analyze your comment. "
                            "Please try again."
                        )
                        st.stop()

            else:
                category = "No Comment"

            save_feedback(
                comment=guest_comment.strip(),
                rating=(
                    guest_rating + 1
                    if guest_rating is not None
                    else None
                ),
                label=category
            )

            st.success(
                "Thank you for sharing your feedback!"
            )

            if guest_comment.strip():
                st.write(
                    "Feedback category:",
                    category
                )


# --------------------------------------------------
# TAB 2: HOTEL MANAGEMENT DASHBOARD
# --------------------------------------------------

with tab_owner:

    st.header("Hotel Management Dashboard")

    st.write(
        "Monitor guest satisfaction and identify "
        "areas that need improvement."
    )

    df = load_feedback()

    # --------------------------------------------------
    # KEY METRICS
    # --------------------------------------------------

    total_feedback = len(df)

    average_rating = (
        pd.to_numeric(
            df["rating"],
            errors="coerce"
        ).mean()
        if not df.empty
        else float("nan")
    )

    manual_review = (
        df[
            (
                (df["label"] == "Other")
                &
                (df["comment"].notna())
                &
                (df["comment"].astype(str).str.strip() != "")
            )
            |
            (
                (df["comment"].notna())
                &
                (df["comment"].astype(str).str.strip() != "")
                &
                (
                    pd.to_numeric(
                        df["rating"],
                        errors="coerce"
                    ) <= 2
                )
            )
        ]
        if not df.empty
        else df
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📝 Total Feedback",
            total_feedback
        )

    with col2:
        st.metric(
            "⭐ Average Rating",
            (
                f"{average_rating:.1f}/5"
                if pd.notna(average_rating)
                else "N/A"
            )
        )

    with col3:
        st.metric(
            "🚩 Needs Manual Review",
            len(manual_review)
        )

    st.divider()

    # --------------------------------------------------
    # GRAPH 1: FEEDBACK BY CATEGORY
    # --------------------------------------------------

    st.subheader("📊 Guest Feedback by Category")

    if not df.empty:

        category_counts = (
            df[
                df["label"].notna()
                &
                (df["label"] != "No Comment")
            ]["label"]
            .value_counts()
            .reset_index()
        )

        category_counts.columns = [
            "Category",
            "Number of Comments"
        ]

        if not category_counts.empty:

            fig_categories = px.bar(
                category_counts,
                x="Category",
                y="Number of Comments",
                title="Most Mentioned Hotel Services",
                text="Number of Comments"
            )

            st.plotly_chart(
                fig_categories,
                use_container_width=True
            )

        else:
            st.info(
                "No written reviews available yet."
            )

    else:
        st.info(
            "No feedback available yet."
        )

    st.divider()

    # --------------------------------------------------
    # GRAPH 2: RATING DISTRIBUTION
    # --------------------------------------------------

    st.subheader("⭐ Guest Rating Distribution")

    ratings = pd.to_numeric(
        df["rating"],
        errors="coerce"
    ).dropna()

    if not ratings.empty:

        rating_counts = (
            ratings.astype(int)
            .value_counts()
            .reindex(range(1, 6), fill_value=0)
            .reset_index()
        )

        rating_counts.columns = [
            "Stars",
            "Number of Reviews"
        ]

        fig_ratings = px.bar(
            rating_counts,
            x="Stars",
            y="Number of Reviews",
            title="Guest Ratings (1–5 Stars)",
            text="Number of Reviews"
        )

        fig_ratings.update_xaxes(
            tickmode="linear",
            dtick=1
        )

        st.plotly_chart(
            fig_ratings,
            use_container_width=True
        )

    else:
        st.info(
            "No star ratings available yet."
        )

    st.divider()

    # --------------------------------------------------
    # COMMENTS REQUIRING MANUAL REVIEW
    # --------------------------------------------------

    st.subheader(
        "🚩 Comments Requiring Manual Review"
    )

    st.write(
        "Comments are flagged when they receive "
        "1–2 stars or are classified as Other."
    )

    if not manual_review.empty:

        st.warning(
            f"{len(manual_review)} comment(s) "
            "require management attention."
        )

        st.dataframe(
            manual_review,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success(
            "No comments currently require manual review."
        )
