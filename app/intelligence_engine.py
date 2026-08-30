
import os
import re
import json
import requests

from urllib.parse import quote
from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parents[1]

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

TELECOM_REGISTRY = load_json(
    PROJECT_PATH / "data/registrations/telecom_registry.json"
)

FINANCIAL_REGISTRY = load_json(
    PROJECT_PATH / "data/registrations/financial_registry.json"
)

SEVERITY_WEIGHT = {
    "INFO": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 4
}


def _registry_records(registry):

    if isinstance(registry, dict):

        if "providers" in registry:
            return registry["providers"]

        if "institutions" in registry:
            return registry["institutions"]

    if isinstance(registry, list):
        return registry

    return []


def extract_message_entities(text):

    text = str(text)

    urls = re.findall(
        r"https?://[^\s<>\"']+",
        text,
        flags=re.IGNORECASE
    )

    phones = re.findall(
        r"(?<!\d)(?:\+234|0)\d{10}(?!\d)",
        text
    )

    ussd = re.findall(
        r"\*\d+(?:\*\d+)*#",
        text
    )

    credentials = [
        term for term in [
            "otp",
            "pin",
            "password",
            "passcode",
            "bvn",
            "nin",
            "cvv"
        ]
        if re.search(rf"\b{re.escape(term)}\b", text, re.I)
    ]

    return {
        "urls": urls,
        "phone_numbers": phones,
        "ussd_codes": ussd,
        "credential_terms": credentials
    }


def resolve_sender(sender_id):

    if not sender_id:
        return {
            "status": "UNKNOWN",
            "institution": None
        }

    candidate = sender_id.strip().lower()

    for registry_name, registry in [
        ("telecom", TELECOM_REGISTRY),
        ("financial", FINANCIAL_REGISTRY)
    ]:

        for record in _registry_records(registry):

            identity = record.get(
                "identity",
                record
            )

            sender_section = record.get(
                "sender_identity",
                {}
            )

            candidates = []

            for key in [
                "canonical_name",
                "aliases",
                "brand_names"
            ]:

                value = identity.get(key, [])

                if isinstance(value, str):
                    candidates.append(value)

                elif isinstance(value, list):
                    candidates.extend(value)

            values = sender_section.get(
                "sender_ids",
                []
            )

            if isinstance(values, list):
                candidates.extend(values)

            for value in candidates:

                if str(value).lower() == candidate:

                    return {
                        "status": "MATCHED",
                        "registry": registry_name,
                        "institution": identity.get(
                            "canonical_name"
                        ),
                        "entity_id": identity.get(
                            "entity_id"
                        )
                    }

    return {
        "status": "UNKNOWN",
        "institution": None
    }


def check_url_ipqs(url):

    api_key = os.getenv("IPQS_API_KEY")

    if not api_key:
        return {
            "available": False,
            "reason": "API key unavailable"
        }

    try:

        encoded = quote(url, safe="")

        endpoint = (
            "https://www.ipqualityscore.com/"
            f"api/json/url/{api_key}/{encoded}"
        )

        response = requests.get(
            endpoint,
            timeout=8
        )

        response.raise_for_status()

        return {
            "available": True,
            "data": response.json()
        }

    except Exception as exc:

        return {
            "available": False,
            "reason": str(exc)
        }


def check_phone_ipqs(phone):

    api_key = os.getenv("IPQS_API_KEY")

    if not api_key:
        return {
            "available": False,
            "reason": "API key unavailable"
        }

    try:

        encoded = quote(phone, safe="")

        endpoint = (
            "https://www.ipqualityscore.com/"
            f"api/json/phone/{api_key}/{encoded}"
        )

        response = requests.get(
            endpoint,
            timeout=8
        )

        response.raise_for_status()

        data = response.json()

        fields = [
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
            "request_id"
        ]

        return {
            "available": True,
            "data": {
                field: data.get(field)
                for field in fields
            }
        }

    except Exception as exc:

        return {
            "available": False,
            "reason": str(exc)
        }


def map_url_evidence(result):

    if not result.get("available"):
        return []

    data = result.get("data", {})
    evidence = []

    mapping = [
        ("phishing", "HIGH", "phishing_detected"),
        ("malware", "HIGH", "malware_detected"),
        ("unsafe", "HIGH", "unsafe_url"),
        ("suspicious", "MEDIUM", "suspicious_url"),
        ("parking", "MEDIUM", "parked_domain"),
        ("short_link_redirect", "LOW", "short_link_redirect")
    ]

    for field, severity, signal in mapping:

        if data.get(field) is True:

            evidence.append({
                "type": "URL",
                "severity": severity,
                "signal": signal,
                "source": "IPQS"
            })

    return evidence


def map_phone_evidence(result):

    if not result.get("available"):
        return []

    data = result.get("data", {})
    evidence = []

    mapping = [
        ("recent_abuse", "HIGH", "recent_abuse"),
        ("spammer", "HIGH", "spammer_indicator"),
        ("risky", "MEDIUM", "risky_number"),
        ("VOIP", "LOW", "voip")
    ]

    for field, severity, signal in mapping:

        if data.get(field) is True:

            evidence.append({
                "type": "PHONE",
                "severity": severity,
                "signal": signal,
                "source": "IPQS"
            })

    return evidence


def evidence_strength(evidence):

    return sum(
        SEVERITY_WEIGHT.get(
            item.get("severity"),
            0
        )
        for item in evidence
    )


def resolve_risk(
    evidence=None,
    registry_match=False
):

    evidence = evidence or []

    high = sum(
        1 for item in evidence
        if item.get("severity") == "HIGH"
    )

    strength = evidence_strength(evidence)

    if high >= 2:
        return "HIGH RISK"

    if high >= 1 and strength >= 5:
        return "HIGH RISK"

    if strength >= 2:
        return "SUSPICIOUS"

    if registry_match:
        return "LOW RISK"

    return "UNKNOWN"


def explain_evidence(evidence):

    messages = {

        "phishing_detected":
            "The link has indicators associated with phishing.",

        "malware_detected":
            "The link has indicators associated with malicious software.",

        "unsafe_url":
            "The link has been flagged as unsafe.",

        "suspicious_url":
            "The link has suspicious characteristics.",

        "parked_domain":
            "The domain appears to be parked.",

        "short_link_redirect":
            "The link uses a shortened redirect.",

        "recent_abuse":
            "This number has recent abuse indicators.",

        "spammer_indicator":
            "This number has spam-related reputation indicators.",

        "risky_number":
            "This number has elevated external risk indicators.",

        "voip":
            "The number appears to use a VoIP connection."
    }

    return [
        messages[item["signal"]]
        for item in evidence
        if item.get("signal") in messages
    ]


def recommended_action(risk):

    return {
        "VERIFIED":
            "Verify important requests independently before acting.",

        "LOW RISK":
            "No meaningful warning signs were found. Stay cautious.",

        "UNKNOWN":
            "There is not enough evidence to make a strong call. Verify independently.",

        "SUSPICIOUS":
            "Do not click, pay or share sensitive information until you verify it.",

        "HIGH RISK":
            "Do not click, pay or share sensitive information. Verify through the official channel."
    }.get(
        risk,
        "Verify independently before acting."
    )


def analyze_url(url):

    result = check_url_ipqs(url)

    evidence = map_url_evidence(result)

    risk = resolve_risk(
        evidence=evidence
    )

    return {
        "risk": risk,
        "evidence": evidence,
        "explanation": explain_evidence(evidence),
        "recommended_action": recommended_action(risk)
    }


def analyze_phone(phone):

    result = check_phone_ipqs(phone)

    evidence = map_phone_evidence(result)

    risk = resolve_risk(
        evidence=evidence
    )

    return {
        "risk": risk,
        "evidence": evidence,
        "explanation": explain_evidence(evidence),
        "recommended_action": recommended_action(risk),
        "provider_data": result.get("data", {})
    }


def analyze_sms(message, sender_id=None):

    entities = extract_message_entities(message)

    sender = resolve_sender(sender_id)

    evidence = []

    if sender["status"] == "MATCHED":

        evidence.append({
            "type": "REGISTRY",
            "severity": "INFO",
            "signal": "recognized_sender"
        })

    url_results = []

    for url in entities["urls"]:

        result = check_url_ipqs(url)

        url_results.append(result)

        evidence.extend(
            map_url_evidence(result)
        )

    phone_results = []

    for phone in entities["phone_numbers"]:

        result = check_phone_ipqs(phone)

        phone_results.append(result)

        evidence.extend(
            map_phone_evidence(result)
        )

    risk = resolve_risk(
        evidence=evidence,
        registry_match=(
            sender["status"] == "MATCHED"
        )
    )

    return {
        "risk": risk,
        "sender": sender,
        "entities": entities,
        "evidence": evidence,
        "url_results": url_results,
        "phone_results": phone_results,
        "explanation": explain_evidence(evidence),
        "recommended_action": recommended_action(risk)
    }
