
import json
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st


def safe_text(value):
    """Convert a value into safe display text."""
    if value is None:
        return "Not available"

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)

    return str(value)


def display_value(value):
    """Return a simple user-facing representation."""
    if value is None:
        return "Not available"

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, (dict, list)):
        return safe_text(value)

    return str(value)


def availability_text(result):
    """Describe whether external intelligence was available."""
    if not isinstance(result, dict):
        return "Not available"

    for key in (
        "provider_available",
        "available",
        "external_available",
    ):
        if key in result:
            return "Available" if result[key] else "Not available"

    external = result.get("external_intelligence")

    if isinstance(external, dict):
        if "available" in external:
            return "Available" if external["available"] else "Not available"

    return "Not available"


def get_state(result):
    """Extract ANWAAD's five-state decision."""
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
            value = value.get("state") or value.get("decision")

        if value:
            return str(value).upper()

    return "UNKNOWN"


def state_description(state):
    """Return simple Nigerian-user wording."""
    descriptions = {
        "VERIFIED": (
            "Strong independent evidence supports the claimed context."
        ),
        "LOW RISK": (
            "No meaningful suspicious evidence was found."
        ),
        "UNKNOWN": (
            "There is not enough independent evidence to make a strong call."
        ),
        "SUSPICIOUS": (
            "Some meaningful warning signs were found."
        ),
        "HIGH RISK": (
            "Several strong warning signs or corroborating signals were found."
        ),
    }

    return descriptions.get(
        state,
        "ANWAAD could not make a strong determination."
    )


def state_icon(state):
    """Return the ANWAAD state marker."""
    icons = {
        "VERIFIED": "⚪",
        "LOW RISK": "🟢",
        "UNKNOWN": "🟡",
        "SUSPICIOUS": "🟠",
        "HIGH RISK": "🔴",
    }

    return icons.get(state, "🟡")


def render_state(result):
    """Display the decision state without hiding the report."""
    state = get_state(result)

    st.markdown(
        f"## {state_icon(state)} {state}"
    )

    st.write(state_description(state))


def render_simple_list(title, values):
    """Display a short list when values exist."""
    if not values:
        return

    st.markdown(f"### {title}")

    for value in values:
        st.write(f"• {display_value(value)}")


def render_mapping(title, data, hidden_keys=None):
    """Display a mapping in a readable form."""
    if not isinstance(data, dict) or not data:
        return

    hidden_keys = set(hidden_keys or [])

    visible = {
        key: value
        for key, value in data.items()
        if key not in hidden_keys
    }

    if not visible:
        return

    st.markdown(f"### {title}")

    for key, value in visible.items():

        # Keep nested evidence readable.
        if isinstance(value, dict):
            with st.expander(
                key.replace("_", " ").title(),
                expanded=False
            ):
                render_mapping(
                    "",
                    value,
                    hidden_keys=hidden_keys
                )

        elif isinstance(value, list):
            with st.expander(
                key.replace("_", " ").title(),
                expanded=False
            ):
                for item in value:
                    if isinstance(item, dict):
                        st.json(item)
                    else:
                        st.write(f"• {display_value(item)}")

        else:
            label = key.replace("_", " ").title()
            st.write(f"**{label}:** {display_value(value)}")


def render_evidence(result):
    """Display evidence produced by the runtime."""
    evidence = result.get("evidence")

    if not evidence:
        return

    st.markdown("### Evidence")

    if isinstance(evidence, list):
        for item in evidence:

            if isinstance(item, dict):
                signal = (
                    item.get("signal")
                    or item.get("reason")
                    or item.get("message")
                    or "Evidence"
                )

                severity = item.get("severity")

                if severity:
                    st.write(
                        f"• **{severity}** — {display_value(signal)}"
                    )
                else:
                    st.write(f"• {display_value(signal)}")

            else:
                st.write(f"• {display_value(item)}")

    elif isinstance(evidence, dict):
        render_mapping("", evidence)


def render_explanation(result):
    """Display ANWAAD's reasoning in simple language."""
    explanation = (
        result.get("explanation")
        or result.get("why")
        or result.get("reason")
    )

    if not explanation:
        return

    st.markdown("### Why ANWAAD reached this result")

    if isinstance(explanation, list):
        for item in explanation:
            st.write(f"• {display_value(item)}")
    else:
        st.write(display_value(explanation))


def render_recommended_action(result):
    """Display the recommended next action."""
    action = (
        result.get("recommended_action")
        or result.get("action")
    )

    if not action:
        return

    st.markdown("### What to do")

    st.info(display_value(action))


def render_external_intelligence(result):
    """Display external intelligence without turning it into ANWAAD's verdict."""

    external = (
        result.get("external_intelligence")
        or result.get("provider_data")
        or result.get("external")
    )

    if not external:
        return

    if isinstance(external, dict):

        # Some runtime responses wrap the provider response.
        provider = external.get("provider", "IPQS")
        available = external.get("available")

        st.markdown("### External Intelligence")

        st.caption(
            f"Provider: {provider}"
        )

        if available is False:
            st.warning(
                "External intelligence is currently unavailable. "
                "This does not mean the item is safe."
            )
            return

        if available is True:
            st.write("**External check:** Available")

        data = external.get("data")

        if isinstance(data, dict):
            render_ipqs_fields(data)
        else:
            render_mapping(
                "",
                external,
                hidden_keys={
                    "provider",
                    "available",
                    "data",
                    "reason",
                }
            )

    else:
        st.markdown("### External Intelligence")
        st.write(display_value(external))


def render_ipqs_fields(data):
    """Display useful IPQS fields without inventing missing values."""

    field_groups = {
        "URL Intelligence": [
            "domain",
            "domain_age",
            "dns_valid",
            "domain_trust",
            "domain_reputation",
            "category",
            "website_category",
            "risky_tld",
            "parking",
            "parked",
            "phishing",
            "malware",
            "suspicious",
            "spam",
            "unsafe",
            "redirects",
            "risk_score",
            "fraud_score",
            "success",
        ],
        "Phone Intelligence": [
            "formatted",
            "valid",
            "country",
            "carrier",
            "line_type",
            "fraud_score",
            "recent_abuse",
            "risky",
            "VOIP",
            "prepaid",
            "active",
            "active_status",
            "spammer",
            "user_activity",
            "leaked",
            "sms_pumping",
            "request_id",
        ],
    }

    # Decide which fields actually exist.
    existing = set(data.keys())

    if existing.intersection(field_groups["URL Intelligence"]):
        st.markdown("#### URL findings")

        for field in field_groups["URL Intelligence"]:
            if field in data:
                label = field.replace("_", " ").title()
                st.write(
                    f"**{label}:** {display_value(data[field])}"
                )

    if existing.intersection(field_groups["Phone Intelligence"]):
        st.markdown("#### Phone findings")

        for field in field_groups["Phone Intelligence"]:
            if field in data:
                label = field.replace("_", " ").title()
                st.write(
                    f"**{label}:** {display_value(data[field])}"
                )

    # Preserve useful provider fields that are not in the initial list.
    known = set(
        field_groups["URL Intelligence"]
        + field_groups["Phone Intelligence"]
    )

    remaining = {
        key: value
        for key, value in data.items()
        if key not in known
    }

    if remaining:
        with st.expander("Other provider findings"):
            render_mapping("", remaining)


def render_extracted_content(result):
    """Display entities ANWAAD extracted from the input."""
    entities = (
        result.get("entities")
        or result.get("extracted_entities")
        or result.get("extractions")
    )

    if not entities:
        return

    st.markdown("### What ANWAAD found inside")

    if isinstance(entities, dict):
        render_mapping("", entities)
    else:
        st.write(display_value(entities))


def render_registry_context(result):
    """Display registry/context findings."""
    context = (
        result.get("context")
        or result.get("registry")
        or result.get("registry_matches")
        or result.get("sender")
    )

    if not context:
        return

    st.markdown("### Registered context")

    if isinstance(context, dict):
        render_mapping("", context)
    elif isinstance(context, list):
        for item in context:
            st.write(f"• {display_value(item)}")
    else:
        st.write(display_value(context))


def render_patterns(result):
    """Display observation/pattern evidence."""
    patterns = (
        result.get("patterns")
        or result.get("pattern_evidence")
        or result.get("observations")
        or result.get("observation_evidence")
    )

    if not patterns:
        return

    st.markdown("### Pattern evidence")

    if isinstance(patterns, list):
        for item in patterns:
            st.write(f"• {display_value(item)}")
    elif isinstance(patterns, dict):
        render_mapping("", patterns)
    else:
        st.write(display_value(patterns))


def render_ml(result):
    """Display ML evidence separately from other evidence."""
    ml = (
        result.get("ml")
        or result.get("ml_result")
        or result.get("model")
    )

    probability = result.get("ml_probability")

    if isinstance(result.get("state"), dict):
        probability = (
            result["state"].get("ml_probability")
            if result["state"].get("ml_probability") is not None
            else probability
        )

    if ml is None and probability is None:
        return

    st.markdown("### Model evidence")

    if probability is not None:
        st.write(
            f"**Calibrated model probability:** "
            f"{float(probability):.4f}"
        )

    if isinstance(ml, dict):
        render_mapping("", ml)


def render_report(result):
    """Render the complete ANWAAD contextual report."""

    render_state(result)

    st.divider()

    render_explanation(result)

    render_registry_context(result)

    render_extracted_content(result)

    render_patterns(result)

    render_evidence(result)

    render_external_intelligence(result)

    render_ml(result)

    render_recommended_action(result)


def render_feedback(feedback_key):
    """Collect feedback without training from it."""
    st.divider()

    st.markdown("### Was this analysis helpful?")

    choice = st.radio(
        "Feedback",
        ["Correct", "Wrong", "Not sure"],
        horizontal=True,
        key=feedback_key,
        label_visibility="collapsed",
    )

    if st.button(
        "Send feedback",
        key=f"{feedback_key}_submit"
    ):
        st.success(
            "Thanks. Your feedback will be reviewed separately."
        )


def render_phone_warning():
    st.info(
        "Stay cautious. Don't send money or share sensitive "
        "information just because the caller sounds convincing."
    )
