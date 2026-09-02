import streamlit as st


def render_footer():
    st.divider()

    st.markdown(
        "### Think you've been defrauded or targeted by cybercrime? "
        "Get official help"
    )

    st.markdown(
        "[Cybercrime → NPF-NCCC](https://nccc.npf.gov.ng/)  \n"
        "[Cyber incident → ngCERT](https://ngcert.gov.ng/)  \n"
        "[Digital-lending complaint → FCCPC](https://complaints.fccpc.gov.ng/)"
    )

    st.markdown(
        "**Stay sharp**  \n"
        "Don't share OTPs, PINs or passwords.  \n"
        "Check your account directly before confirming payment."
    )

    st.caption(
        "ANWAAD v0.1 — Context intelligence for suspicious SMS messages, "
        "links and phone numbers."
    )
