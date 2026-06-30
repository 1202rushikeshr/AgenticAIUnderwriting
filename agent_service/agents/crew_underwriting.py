import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

load_dotenv()

# ---------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------

llm = LLM(
    model=os.getenv(
        "MODEL",
        "bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
    ),
    temperature=0.2,
    max_tokens=2048,
)

# ---------------------------------------------------------------------
# TOOLS (STRICT STRING INPUTS)
# ---------------------------------------------------------------------

@tool("Eligibility Rule Engine")
def eligibility_rule_tool(applicant_json: str) -> str:
    """Deterministic eligibility rules."""
    data = json.loads(applicant_json)

    age = int(data.get("age", 0))
    income = int(data.get("income", 0))
    prior_claims = int(data.get("prior_claims", 0))
    smoking_status = str(data.get("smoking_status", "")).lower()

    reasons = []
    if age < 18 or age > 65:
        reasons.append("Age not in range 18–65")
    if income < 20000:
        reasons.append("Income below minimum threshold")
    if prior_claims > 5:
        reasons.append("Too many prior claims")
    if smoking_status == "smoker" and age > 55:
        reasons.append("High-risk smoker")

    return json.dumps({
        "eligible": len(reasons) == 0,
        "reasons": reasons
    })


@tool("Risk Scoring Engine")
def risk_scoring_tool(payload_json: str) -> str:
    """Compute numeric risk score."""
    if not isinstance(payload_json, str):
        raise ValueError("payload_json MUST be a JSON string")

    data = json.loads(payload_json)

    applicant = data["applicant"]
    coverage = int(data["coverage_amount"])

    score = 0
    if applicant.get("age", 0) > 50:
        score += 20
    if applicant.get("income", 0) < 50000:
        score += 10
    if applicant.get("prior_claims", 0) > 0:
        score += applicant["prior_claims"] * 15
    if applicant.get("smoking_status", "") == "smoker":
        score += 25
    if coverage >= 500000:
        score += 20

    score = min(score, 100)
    band = "LOW" if score <= 30 else "MEDIUM" if score <= 65 else "HIGH"

    return json.dumps({
        "risk_score": score,
        "decision_band": band
    })


# ---------------------------------------------------------------------
# ENTRYPOINT (CREW CREATED PER REQUEST)
# ---------------------------------------------------------------------

def run_underwriting_crew(
    raw_document_text: str,
    product_type: str,
    coverage_amount: int,
    applicant: Dict[str, Any], 
) -> Dict[str, Any]:

    # ----------------- Agents -----------------
    document_agent = Agent(
    role="Applicant Data Normalizer",
    goal="Normalize applicant data provided by backend without modification",
    backstory="Strict data normalizer. Never invents values.",
    llm=llm,
    verbose=True,
)


    eligibility_agent = Agent(
        role="Eligibility Rules Underwriter",
        goal="Validate applicant eligibility",
        backstory="Strict underwriting rules expert",
        llm=llm,
        tools=[eligibility_rule_tool],
        verbose=True,
    )

    risk_agent = Agent(
        role="Risk Assessment Analyst",
        goal="Compute numeric underwriting risk score using the tool only.",
        backstory="Strict actuarial engine. Never improvises inputs.",
        llm=llm,
        tools=[risk_scoring_tool],
        allow_delegation=False,
        verbose=True,
    )


    decision_agent = Agent(
        role="Underwriting Decision Maker",
        goal="Make final underwriting decision",
        backstory="Senior underwriting authority",
        llm=llm,
        verbose=True,
    )

    # ----------------- Tasks -----------------
    document_task = Task(
    description=(
        "You are given:\n"
        "1) `applicant`: a JSON object provided by the backend (AUTHORITATIVE).\n"
        "2) `product_type`\n"
        "3) `coverage_amount`\n\n"

        "STRICT RULES:\n"
        "- The `applicant` object is the single source of truth.\n"
        "- You MUST NOT invent or infer applicant data.\n"
        "- You MUST NOT extract applicant data from document_text.\n"
        "- If a field is missing, set it to null.\n\n"

        "Return a normalized JSON object named `applicant_record`:\n"
        "{ name, age, income, occupation, location, prior_claims, "
        "smoking_status, product_type, coverage_amount }"
    ),
    expected_output="JSON applicant_record",
    agent=document_agent,
)


    eligibility_task = Task(
        description="Return JSON {eligible, reasons}",
        expected_output="Eligibility JSON",
        agent=eligibility_agent,
    )

    risk_task = Task(
        description=(
            "You MUST call the Risk Scoring Engine tool.\n"
            "You MUST pass ONLY this argument:\n\n"
             "payload_json = JSON STRING with EXACT structure:\n"
             "{\n"
            '  "applicant": <full applicant JSON>,\n'
            '  "coverage_amount": <number>\n'
            "}\n\n"
            "DO NOT add any other keys.\n"
            "DO NOT use description.\n"
            "Return ONLY the tool output."
        ),
        expected_output="JSON {risk_score, decision_band}",
        agent=risk_agent,
    )
 
    decision_task = Task(
        description=(
            "Based on eligibility and risk score:\n"
            "- APPROVE if eligible=true and risk_score <= 30\n"
            "- REFER if eligible=true and risk_score between 31–65\n"
            "- DECLINE if eligible=false or risk_score > 65\n\n"
            "Return ONLY JSON:\n"
            "{ decision: 'APPROVE|REFER|DECLINE', reasoning: string, risk_score: number }"
        ),
        expected_output="Decision JSON",
        agent=decision_agent,
    )


    crew = Crew(
        agents=[
            document_agent,
            eligibility_agent,
            risk_agent,
            decision_agent,
        ],
        tasks=[
            document_task,
            eligibility_task,
            risk_task,
            decision_task,
        ],
        process=Process.sequential,
        verbose=True,
    )

    # ----------------- Run -----------------
    crew.kickoff(
        inputs={
            "document_text": raw_document_text,
            "product_type": product_type,
            "coverage_amount": coverage_amount,
            "applicant": applicant,
        }
    )

    # ----------------- SAFE OUTPUT PARSING -----------------
    eligibility = json.loads(eligibility_task.output.raw_output)
    risk = json.loads(risk_task.output.raw_output)
    decision = json.loads(decision_task.output.raw_output)

    return {
        "decision": decision["decision"],
        "reasoning": decision["reasoning"],
        "risk_score": risk["risk_score"],
        "decision_band": risk["decision_band"],
        "eligible": eligibility["eligible"],
    }
