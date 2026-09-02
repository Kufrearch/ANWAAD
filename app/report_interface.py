
def render_last_result():
    result = st.session_state.get("last_result")

    if not isinstance(result, dict):
        return

    kind = st.session_state.get(
        "last_kind",
        "analysis"
    )

    st.divider()

    st.markdown("## ANWAAD's findings")

    render_report(result)

    if kind == "phone":
        render_phone_warning()
