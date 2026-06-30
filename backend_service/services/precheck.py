def calculate_precheck_risk(applicant, coverage_amount: int):
    score = 0
    reasons = []

    if applicant.age > 50:
        score += 20
        reasons.append("Age above 50")

    if applicant.income < 50000:
        score += 10
        reasons.append("Low income")

    if applicant.prior_claims > 0:
        score += applicant.prior_claims * 15
        reasons.append("Prior claims history")

    if applicant.smoking_status == "smoker":
        score += 25
        reasons.append("Smoking risk")

    if coverage_amount >= 500000:
        score += 20
        reasons.append("High coverage amount")

    score = min(score, 100)

    if score <= 30:
        decision = "APPROVE"
    elif score <= 65:
        decision = "REFER"
    else:
        decision = "DECLINE"

    return score, decision, reasons
