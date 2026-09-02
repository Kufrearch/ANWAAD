
def render_feedback_for_result():
    if "last_result" not in st.session_state:
        return

    render_feedback("analysis_feedback")

    if st.session_state.get("last_kind") == "phone":
        st.divider()

        st.markdown(
            "### Have you personally received suspicious activity "
            "from this number?"
        )

        phone_feedback = st.radio(
            "Phone feedback",
            ["Yes", "No", "Not sure"],
            horizontal=True,
            key="phone_feedback",
            label_visibility="collapsed",
        )

        if st.button(
            "Send number feedback",
            key="phone_feedback_submit",
        ):
            st.success(
                "Thanks. Your feedback will be reviewed separately."
            )
