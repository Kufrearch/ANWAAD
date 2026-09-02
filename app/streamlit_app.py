
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import the one authoritative intelligence engine.
from intelligence_engine import (
    analyze_sms,
    analyze_url,
    analyze_phone,
)

from app.ui_helpers import (
    render_report,
    render_feedback,
    render_phone_warning,
)

from app.footer import render_footer


st.set_page_config(
    page_title="ANWAAD",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# Keep the product name separate from the model release.
st.title("ANWAAD")
st.caption("Context Intelligence Engine · v0.1")

st.write(
    "Inspect suspicious messages, websites and phone numbers "
    "using multiple sources of evidence."
)


mode = st.radio(
    "What do you want to check?",
    [
        "Analyze SMS",
        "Check URL",
        "Check Number",
    ],
    horizontal=True,
)


def get_state(result):
    if not isinstance(result, dict):
        return "UNKNOWN"

    state = result.get("state")

    if isinstance(state, dict):
        state = state.get("state")

    if state:
        return str(state).upper()

    for key in ("decision", "risk", "status"):
        value = result.get(key)

        if isinstance(value, dict):
            value = (
                value.get("state")
                or value.get("decision")
                or value.get("risk")
            )

        if value:
            return str(value).upper()

    return "UNKNOWN"


def state_icon(state):
    return {
        "VERIFIED": "⚪",
        "LOW RISK": "🟢",
        "UNKNOWN": "🟡",
        "SUSPICIOUS": "🟠",
        "HIGH RISK": "🔴",
    }.get(state, "🟡")


def state_text(state):
    return {
        "VERIFIED":
            "Strong independent evidence supports this context.",
        "LOW RISK":
            "No meaningful suspicious evidence was found.",
        "UNKNOWN":
            "There is not enough independent evidence to make a strong call.",
        "SUSPICIOUS":
            "Some meaningful warning signs were found.",
        "HIGH RISK":
            "Several strong warning signs or corroborating signals were found.",
    }.get(
        state,
        "ANWAAD could not make a strong determination."
    )


def show_result(result, kind):
    st.divider()

    state = get_state(result)

    st.markdown(
        f"## {state_icon(state)} {state}"
    )

    st.write(state_text(state))

    st.divider()

    render_report(result)

    if kind == "phone":
        render_phone_warning()

    st.divider()

    st.markdown("### Was this analysis helpful?")

    feedback = st.radio(
        "Analysis feedback",
        ["Correct", "Wrong", "Not sure"],
        horizontal=True,
        key=f"feedback_{kind}",
        label_visibility="collapsed",
    )

    if st.button(
        "Send feedback",
        key=f"feedback_submit_{kind}",
    ):
        # Feedback is acknowledged but not used for automatic retraining.
        st.success(
            "Thanks. Your feedback will be reviewed separately."
        )


if mode == "Analyze SMS":

    st.subheader("Analyze an SMS")

    sender_id = st.text_input(
        "Sender ID (optional but recommended)",
        placeholder="Example: 312, KEYSTONE, MTN N, MoMoPSB",
        help=(
            "Enter the exact Sender ID shown at the top of the SMS."
        ),
    )

    st.caption(
        "Use the exact Sender ID shown above the message. "
        "Do not type the company name based on assumption."
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
        else:
            try:
                with st.spinner(
                    "ANWAAD is inspecting the message..."
                ):
                    result = analyze_sms(
                        message.strip(),
                        sender_id=sender_id.strip() or None,
                    )

                show_result(result, "sms")

            except Exception:
                st.error(
                    "ANWAAD could not complete the analysis. "
                    "Please try again."
                )


elif mode == "Check URL":

    st.subheader("Check a URL")

    st.caption(
        "You can enter the website with or without https://"
    )

    url = st.text_input(
        "Website link",
        placeholder="github.com",
    )

    if st.button(
        "Check URL",
        type="primary",
        use_container_width=True,
    ):
        if not url.strip():
            st.warning("Enter a URL first.")
        else:
            try:
                with st.spinner(
                    "ANWAAD is checking the URL..."
                ):
                    result = analyze_url(url.strip())

                show_result(result, "url")

            except Exception:
                st.error(
                    "ANWAAD could not complete the URL analysis. "
                    "Please check the URL and try again."
                )


else:

    st.subheader("Check a phone number")

    st.caption(
        "ANWAAD checks observable evidence about the number. "
        "A phone number does not prove who a person is."
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
        else:
            try:
                with st.spinner(
                    "ANWAAD is checking the number..."
                ):
                    result = analyze_phone(number.strip())

                show_result(result, "phone")

            except Exception:
                st.error(
                    "ANWAAD could not complete the number analysis. "
                    "Please try again."
                )


render_footer()
