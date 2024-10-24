# Compliance Check

## Installation
1. Clone the repository:
```
git clone https://github.com/Akshat-bhatia73/compliance_check.git
cd compliance-checker
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Set up environment variables:
- Create a .env file:
```
FIREWORKS_API_KEY=fireworks_api_key_here
```

## Usage

1. API Endpoint `POST /check-compliance`
- Request body:
```
{
    "url": "https://mercury.com/",
    "policy_url": "https://stripe.com/docs/treasury/marketing-treasury"
}
```

- Response:
```
{
    "url_analyzed": "https://mercury.com/",
    "checked_against": "https://stripe.com/docs/treasury/marketing-treasury",
    "compliance_result": {
        "violations": [
            {
                "policy_section": "Marketing Treasury-based services",
                "violation_description": "The webpage content contains the term 'Online Business Banking For Startups', which may draw scrutiny from regulators as it potentially implies that the service is a bank account offered by a state- or federally-chartered bank or credit union. It is recommended to use terms like 'Money management' or 'Cash management' instead.",
                "example": "Online Business Banking For Startups | Simplified Financial Workflows",
                "recommended_fix": "Modify the term 'Online Business Banking For Startups' to 'Money Management for Startups' or 'Cash Management for Startups' to ensure compliance with regulations.",
                "severity": "medium"
            },
            {
                "policy_section": "Marketing Treasury-based services",
                "violation_description": "The webpage content contains the term 'Banking services provided by Choice Financial Group, Column N.A., and Evolve Bank & Trust®; Members FDIC.' This statement may imply that the service is a bank account offered by a state- or federally-chartered bank or credit union. It is recommended to use terms like 'Financial services provided by...' instead.",
                "example": "Banking services provided by Choice Financial Group, Column N.A., and Evolve Bank & Trust®; Members FDIC.",
                "recommended_fix": "Modify the term 'Banking services' to 'Financial services' to ensure compliance with regulations.",
                "severity": "medium"
            },
            {
                "policy_section": "Yield compliance marketing guidance",
                "violation_description": "The webpage content does not disclose prominently that the yield percentage is subject to change and the conditions under which it might change. This is a requirement for marketing disclosures related to yield.",
                "example": "Earn up to 4.88 % yield on your idle cash with portfolios powered by Vanguard and Morgan Stanley",
                "recommended_fix": "Add a disclaimer near the yield percentage that states 'The yield percentage is subject to change and the conditions under which it might change.' This will ensure compliance with regulations.",
                "severity": "high"
            }
        ],
        "total_violations": 3,
        "summary": "The webpage content contains 3 compliance violations related to marketing Treasury-based services and yield compliance marketing guidance. It is recommended to modify the terms 'Online Business Banking For Startups' and 'Banking services' to ensure compliance with regulations. Additionally, a disclaimer related to the yield percentage should be added to the content."
    }
}
```