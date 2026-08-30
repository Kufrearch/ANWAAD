# ANWAAD

ANWAAD is a context intelligence engine for analyzing potentially fraudulent
SMS messages, URLs and phone numbers.

## Model

ANWAAD v0.1

The ML classifier is only one evidence source. Final decisions combine:

- ML evidence
- telecom registry evidence
- financial registry evidence
- message/entity evidence
- URL intelligence
- phone intelligence
- contextual evidence
- contradiction handling

## Analysis Modes

### Analyze Message
Analyzes:
- message content
- sender identity
- URLs
- phone numbers
- USSD codes
- credential-related language
- financial context

### Verify URL
Allows a URL to be analyzed independently.

### Check Number
Allows a phone number to be analyzed independently.

## Risk States

- VERIFIED
- LOW RISK
- UNKNOWN
- SUSPICIOUS
- HIGH RISK

Unknown does not mean safe.
Low risk does not mean guaranteed safe.
A valid phone number does not mean the operator is trustworthy.

## Privacy

ANWAAD should not unnecessarily persist:

- raw SMS
- account numbers
- phone numbers
- OTPs
- PINs
- passwords
- BVN
- NIN
- personal identity information

## External Intelligence

IPQS is treated as an external evidence provider.

Its scores are not presented as the ANWAAD verdict.

## Feedback

User feedback is collected separately and must be reviewed before it becomes
training data.

## Development

The model-training notebook is:

ANWAAD_Model_Build_Pipeline.ipynb
