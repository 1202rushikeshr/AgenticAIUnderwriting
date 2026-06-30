from crewai import Task
from .underwriting_agents import (
    document_agent,
    eligibility_agent,
    risk_agent,
    decision_agent,
    notification_agent,
)

# -------------------------------------------------------------------
# Task 1: Normalize applicant data (NO inference, NO hallucination)
# -------------------------------------------------------------------
extract_task = Task(
    description=(
        "You are given the following runtime inputs:\n\n"

        "APPLICANT (AUTHORITATIVE JSON):\n"
        "{applicant}\n\n"

        "PRODUCT TYPE:\n"
        "{product_type}\n\n"

        "COVERAGE AMOUNT:\n"
        "{coverage_amount}\n\n"

        "STRICT RULES:\n"
        "- The applicant JSON above is the single source of truth.\n"
        "- You MUST NOT invent, infer, or modify applicant fields.\n"
        "- You MUST NOT generate placeholder names (e.g., John Doe).\n"
        "- If a value is missing, keep it null.\n\n"

        "Return a normalized JSON object named `applicant_record` with:\n"
        "name, age, income, occupation, location, prior_claims, "
        "smoking_status, product_type, coverage_amount."
    ),
    agent=document_agent,
    expected_output="JSON applicant_record",
)

# -------------------------------------------------------------------
# Task 2: Eligibility evaluation (NO data invention)
# -------------------------------------------------------------------
eligibility_task = Task(
    description=(
        "Using ONLY the provided `applicant_record` JSON, "
        "evaluate eligibility based on these rules:\n\n"
        "- Age must be between 18 and 65 inclusive.\n"
        "- Income must be at least 20000.\n"
        "- Prior claims must be <= 5.\n"
        "- If smoking_status is 'smoker' and age > 55, mark as high risk.\n\n"

        "IMPORTANT RULES:\n"
        "- Do NOT invent applicant data.\n"
        "- If any required field is null, explain this clearly in reasons.\n"
        "- Use ONLY values from `applicant_record`.\n\n"

        "Return a JSON object named `eligibility_result`:\n"
        '{ "status": "PASS|FAIL|REFER", "reasons": [string] }'
    ),
    agent=eligibility_agent,
    expected_output=(
        'JSON: { "status": "PASS|FAIL|REFER", "reasons": [ ... ] }'
    ),
)

# -------------------------------------------------------------------
# Task 3: Risk scoring (tool-driven, strict payload)
# -------------------------------------------------------------------
risk_task = Task(
    description=(
        "Compute risk score using ONLY the provided `applicant_record` "
        "and `coverage_amount`.\n\n"

        "You MUST call the Risk Scoring Engine tool.\n\n"

        "IMPORTANT RULES:\n"
        "- Do NOT invent or modify applicant fields.\n"
        "- Use values exactly as provided.\n"
        "- Do NOT change payload structure.\n\n"

        "When calling the tool, you MUST pass:\n"
        "payload_json = JSON string with this EXACT structure:\n\n"
        "{\n"
        '  "applicant": <applicant_record>,\n'
        '  "coverage_amount": <number>\n'
        "}\n\n"

        "Return ONLY JSON:\n"
        '{ "risk_score": number, "decision_band": string }'
    ),
    expected_output="Risk JSON",
    agent=risk_agent,
)

# -------------------------------------------------------------------
# Task 4: Final underwriting decision
# -------------------------------------------------------------------
decision_task = Task(
    description=(
        "You are given:\n"
        "- `eligibility_result`\n"
        "- `risk_score` (from AI risk engine)\n\n"

        "You are ALSO given preliminary underwriting results from backend rules:\n"
        "- Preliminary Risk Score: {pre_risk_score}\n"
        "- Preliminary Decision: {pre_decision}\n"
        "- Preliminary Reasoning: {pre_reasoning}\n\n"

        "DECISION RULES:\n"
        "- APPROVE if eligibility_result.status = PASS and risk_score <= 30\n"
        "- REFER if eligibility_result.status = PASS and risk_score between 31–65\n"
        "- DECLINE if eligibility_result.status = FAIL or risk_score > 65\n\n"

        "IMPORTANT:\n"
        "- Treat preliminary decision as a baseline signal.\n"
        "- You MAY agree or disagree with the preliminary decision.\n"
        "- If you disagree, clearly explain WHY in reasoning.\n"
        "- The FINAL decision must be consistent and well-justified.\n\n"

        "Return ONLY JSON:\n"
        "{\n"
        '  "decision": "APPROVE|REFER|DECLINE",\n'
        '  "reasoning": string,\n'
        '  "risk_score": number\n'
        "}"
    ),
    expected_output="Decision JSON",
    agent=decision_agent,
)

# -------------------------------------------------------------------
# Task 5: Notifications (NO fake names)
# -------------------------------------------------------------------
notification_task = Task(
    description=(
        "Using the FINAL underwriting decision JSON:\n"
        "{ decision, risk_score, reasoning }\n\n"
        "AND the applicant_record, generate notifications.\n\n"

        "IMPORTANT:\n"
        "- You MUST pass through decision and risk_score unchanged.\n"
        "- Do NOT remove or rename fields.\n\n"

        "Return ONLY JSON:\n"
        "{\n"
        '  "decision": "APPROVE|REFER|DECLINE",\n'
        '  "risk_score": number,\n'
        '  "reasoning": string,\n'
        '  "notifications": [\n'
        '    { "recipient": string, "channel": string, "message": string }\n'
        "  ]\n"
        "}"
    ),
    expected_output=(
        "JSON object containing decision, risk_score, reasoning, "
        "and notifications list"
    ),
    agent=notification_agent,
)

   