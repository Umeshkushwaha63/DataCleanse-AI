import streamlit as st
import pandas as pd


def show_home():
    """Render the DataCleanse AI home dashboard."""

    st.title("🎵 DataCleanse AI")

    st.markdown(
        "### Intelligent Data Cleaning & Business Intelligence"
    )

    st.write(
        "Upload your dataset, clean it safely with AI, "
        "generate SQL, and discover business insights."
    )

    st.divider()

    # -----------------------------
    # Dashboard Metrics
    # -----------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="New Subscribers",
            value="12,482",
            delta="+8.4%"
        )

    with col2:
        st.metric(
            label="Active Users",
            value="48,920",
            delta="+5.2%"
        )

    with col3:
        st.metric(
            label="Revenue",
            value="₹24.8L",
            delta="+12.6%"
        )

    with col4:
        st.metric(
            label="Data Quality",
            value="94.8%",
            delta="+3.1%"
        )

    st.divider()

    # -----------------------------
    # Quick Actions
    # -----------------------------

    st.subheader("Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "📂 Upload Dataset",
            use_container_width=True
        ):
            st.session_state["page"] = "Upload"

    with col2:
        if st.button(
            "🧹 AI Cleaning",
            use_container_width=True
        ):
            st.session_state["page"] = "AI Cleaning"

    with col3:
        if st.button(
            "📊 Analytics",
            use_container_width=True
        ):
            st.session_state["page"] = "Analytics"

    st.divider()

    # -----------------------------
    # Subscriber Overview
    # -----------------------------

    st.subheader("👥 Subscriber Overview")

    subscriber_data = pd.DataFrame(
        {
            "Plan": [
                "Premium",
                "Family",
                "Student",
                "Free"
            ],
            "Subscribers": [
                5240,
                3120,
                2860,
                1262
            ]
        }
    )

    st.bar_chart(
        subscriber_data.set_index("Plan")
    )

    st.divider()

    # -----------------------------
    # Top Customers
    # -----------------------------

    st.subheader("🏆 Top Customers")

    customers = pd.DataFrame(
        {
            "Customer": [
                "Customer 001",
                "Customer 002",
                "Customer 003",
                "Customer 004",
                "Customer 005"
            ],
            "Plan": [
                "Premium",
                "Family",
                "Premium",
                "Student",
                "Premium"
            ],
            "Revenue": [
                "₹12,499",
                "₹10,850",
                "₹9,720",
                "₹8,450",
                "₹7,920"
            ]
        }
    )

    st.dataframe(
        customers,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------
    # Recent Activity
    # -----------------------------

    st.subheader("🕐 Recent Activity")

    activities = [
        "New Premium subscription",
        "Dataset cleaned successfully",
        "AI generated SQL query",
        "Data quality report generated",
        "New subscriber added",
    ]

    for activity in activities:
        st.write(f"• {activity}")