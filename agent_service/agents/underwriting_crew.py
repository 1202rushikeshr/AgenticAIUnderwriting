import json
from typing import Dict, Any
from crewai import Crew, Process
from crewai.crews.crew_output import CrewOutput 
from .underwriting_tasks import (
    extract_task,
    eligibility_task,
    risk_task,
    decision_task,
    notification_task,
)

underwriting_crew = Crew(
    agents=[
        extract_task.agent,
        eligibility_task.agent,
        risk_task.agent,
        decision_task.agent,
        notification_task.agent,
    ],
    tasks=[
        extract_task,
        eligibility_task,
        risk_task,
        decision_task,
        notification_task,
    ],
    process=Process.sequential,
    verbose=True,
)

def run_underwriting_crew(
    raw_document_text: str,
    product_type: str,
    coverage_amount: int,
    applicant: Dict[str, Any],
    pre_risk_score: float,
    pre_decision: str,
    pre_reasoning: str,
) -> Dict[str, Any]:

    kickoff_input = {
        "document_text": raw_document_text,
        "product_type": product_type,
        "coverage_amount": coverage_amount,
        "applicant": applicant,
        "pre_risk_score": pre_risk_score,
        "pre_decision": pre_decision,
        "pre_reasoning": pre_reasoning,
    }

    print("🚀 KICKOFF INPUT:", kickoff_input)

    result = underwriting_crew.kickoff(inputs=kickoff_input)

    # ✅ MOST ROBUST FIX (version-independent)
    if isinstance(result, CrewOutput):
        try:
            # CrewOutput.__str__() prints the final JSON
            return json.loads(str(result))
        except Exception:
            raise ValueError(f"Unable to parse CrewOutput: {result}")

    if isinstance(result, dict):
        return result

    if isinstance(result, str):
        try:
            return json.loads(result)
        except Exception:
            return {"raw_output": result}

    raise ValueError(f"Unexpected Crew output type: {type(result)}")
