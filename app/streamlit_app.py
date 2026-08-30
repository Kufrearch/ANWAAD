
import streamlit as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from intelligence_engine import (
    analyze_sms,
    analyze_url,
    analyze_phone
)

st.set_page_config(
    page_title="ANWAAD",
    page_icon="🛡️",
    layout="centered"
)

st.title("ANWAAD")
st.caption("Context Intelligence Engine · v0.1")

mode = st.radio(
    "What do you want to check?",
    [
        "Analyze Message",
        "Verify URL",
        "Check Number"
    ],
    horizontal=True
)

if mode == "Analyze Message":

    sender = st.text_input(
        "Who sent this? (optional)",
        placeholder="Sender ID or phone number"
    )

    message = st.text_area(
        "Paste the message",
        height=220,
        placeholder="Paste the SMS here..."
    )

    if st.button("Analyze Message", type="primary"):

        if not message.strip():
            st.warning("Paste a message first.")
        else:

            with st.spinner("Analyzing..."):
                result = analyze_sms(
                    message,
                    sender_id=sender or None
                )

            st.subheader(result["risk"])

            if result["explanation"]:
                st.write("### Why")

                for reason in result["explanation"]:
                    st.write("•", reason)

            st.write("### What to do")
            st.write(result["recommended_action"])

            st.divider()

            st.caption(
                "A message can look genuine and still be fraudulent. "
                "Verify important requests independently."
            )


elif mode == "Verify URL":

    url = st.text_input(
        "Paste a link",
        placeholder="https://example.com"
    )

    if st.button("Verify URL", type="primary"):

        if not url.strip():
            st.warning("Paste a URL first.")
        else:

            with st.spinner("Checking link..."):
                result = analyze_url(url.strip())

            st.subheader(result["risk"])

            for reason in result["explanation"]:
                st.write("•", reason)

            st.write("### What to do")
            st.write(result["recommended_action"])


else:

    number = st.text_input(
        "Paste a phone number",
        placeholder="+234..."
    )

    if st.button("Check Number", type="primary"):

        if not number.strip():
            st.warning("Enter a phone number first.")
        else:

            with st.spinner("Checking number..."):
                result = analyze_phone(number.strip())

            st.subheader(result["risk"])

            for reason in result["explanation"]:
                st.write("•", reason)

            st.write("### What we found")

            provider_data = result.get("provider_data", {})

            if provider_data:
                for key in [
                    "valid",
                    "country",
                    "carrier",
                    "line_type",
                    "active",
                    "recent_abuse",
                    "risky"
                ]:
                    value = provider_data.get(key)

                    if value is not None:
                        st.write(
                            f"**{key.replace('_', ' ').title()}:** {value}"
                        )

            st.write("### What to do")
            st.write(result["recommended_action"])

            st.info(
                "Stay cautious. Don't send money or share sensitive "
                "information just because the caller sounds convincing."
            )


st.divider()

st.caption(
    "Think you've been defrauded or targeted by cybercrime? Get official help"
)

st.markdown(
    "Cybercrime → NPF-NCCC  \n"
    "Cyber incident → ngCERT  \n"
    "Digital-lending complaint → FCCPC"
)

st.markdown(
    "**Stay sharp**  \n"
    "Don't share OTPs, PINs or passwords.  \n"
    "Check your account directly before confirming payment."
)
