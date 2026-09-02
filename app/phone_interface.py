
def render_phone_mode():
    st.subheader("Check a phone number")

    st.caption(
        "ANWAAD checks the number as evidence. "
        "A number does not prove who a person is."
    )

    number = st.text_input(
        "Phone number",
        placeholder="+2348012345678",
    )

    if st.button(
        "Check number",
        type="primary",
        use_container_width=True,
    ):
        if not number.strip():
            st.warning("Enter a phone number first.")
            return

        try:
            with st.spinner(
                "ANWAAD is checking the number..."
            ):
                result = analyze_phone(number.strip())

            st.session_state["last_result"] = result
            st.session_state["last_kind"] = "phone"

        except Exception:
            st.error(
                "ANWAAD could not complete the number analysis. "
                "Please try again."
            )
