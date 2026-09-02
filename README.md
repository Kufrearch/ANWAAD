# ANWAAD

ANWAAD is a context intelligence system for analyzing potentially fraudulent SMS messages, URLs, and phone numbers.

## Model

Product Name: ANWAAD
Current model release: ANWAAD v0.1

The product identity remains ANWAAD, while individual model iterations are tracked separately under release versions.

## Analysis System

The machine learning classifier is one component of a broader architecture. Final risk decisions combine:

- message intelligence
- telecom registry evidence
- financial registry evidence
- observed-message patterns
- URL intelligence
- phone intelligence
- machine-learning evidence
- evidence fusion

External provider intelligence is treated as evidence, not as the ANWAAD verdict.

## Analysis Modes

1. **Analyze SMS:** Evaluates complete message text, sender ID, embedded URLs, phone numbers, USSD codes, and financial/credential language.
2. **Check URL:** Inspects website links independently against known domain registries and threat parameters.
3. **Check Number:** Evaluates phone numbers based on observable structural evidence.

## Risk States

- **VERIFIED:** Strong independent evidence supports the entity context.
- **LOW RISK:** No meaningful suspicious evidence was detected.
- **UNKNOWN:** Insufficient evidence exists to make a strong determination.
- **SUSPICIOUS:** Specific warning signs or anomalies were detected.
- **HIGH RISK:** Multiple strong warning signs or corroborating fraud signals detected.

*Important Caveats:*
- `UNKNOWN` does not mean safe.
- `LOW RISK` does not mean guaranteed safe.
- A valid or active phone number does not prove operator identity or intent.

## Data Privacy & Retention

To preserve user privacy, ANWAAD avoids unnecessary persistence or logging of:

- Raw SMS text content
- Account numbers & payment credentials
- One-Time Passwords (OTPs), PINs, or passwords
- Bank Verification Numbers (BVN) or National Identification Numbers (NIN)
- Unnecessary personal phone numbers or identity attributes

## Feedback & Human-in-the-Loop

User feedback collected via the UI is logged independently for audit and manual review. It is never injected into automated model retraining pipelines.

## Development

Model build notebook:

ANWAAD_Model_Build_Pipeline.ipynb
