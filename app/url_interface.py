
def render_url_mode():
    st.subheader("Check a URL")

    st.caption(
        "You can enter a website with or without https://"
    )

    url = st.text_input(
        "Website link",
        placeholder="github.com",
        help=(
            "Examples: github.com, www.github.com, "
            "https://github.com/user/repository"
        ),
    )

    if st.button(
        "Check URL",
        type="primary",
        use_container_width=True,
    ):
        if not url.strip():
            st.warning("Enter a URL first.")
            return

        try:
            with st.spinner(
                "ANWAAD is checking the URL..."
            ):
                result = analyze_url(url.strip())

            st.session_state["last_result"] = result
            st.session_state["last_kind"] = "url"

        except Exception:
            st.error(
                "ANWAAD could not complete the URL analysis. "
                "Please check the URL and try again."
            )
