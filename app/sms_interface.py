
def render_sms_mode():
    st.subheader("Analyze an SMS")

    st.caption(
        "Give ANWAAD the message exactly as you received it."
    )

    sender = st.text_input(
        "Sender ID (optional but recommended)",
        placeholder="Example: 312, KEYSTONE, MTN N, MoMoPSB",
        help=(
            "Enter the exact Sender ID shown at the top of the SMS. "
            "Do not type what you think the sender is."
        ),
    )

    st.caption(
        "Use the exact Sender ID shown above the message. "
        "This helps ANWAAD compare the sender with registered information."
    )

    message = st.text_area(
        "SMS message",
        height=240,
        placeholder="Paste the complete SMS here...",
    )

    if st.button(
        "Analyze message",
        type="primary",
        use_container_width=True,
    ):
        if not message.strip():
            st.warning("Paste an SMS message first.")
            return

        try:
            with st.spinner(
                "ANWAAD is inspecting the message..."
            ):
                result = analyze_sms(
                    message.strip(),
                    sender_id=sender.strip() or None,
                )

            st.session_state["last_result"] = result
            st.session_state["last_kind"] = "sms"

        except Exception:
            st.error(
                "ANWAAD could not complete this analysis. "
                "Please try again."
            )
