from crewai.tools import tool
import json

import json
from crewai.tools import tool


@tool("Notification Dispatcher")
def notification_tool(payload_json: str) -> str:
    """
    Sends notifications to stakeholders.

    Input (payload_json as STRING):
    {
      "event": "UNDERWRITING_DECISION",
      "recipient": "underwriter@app.com",
      "message": "Application APPROVED with risk score 20"
    }

    Output:
    JSON string {"status": "sent"}
    """

    payload = json.loads(payload_json)

    event = payload.get("event")
    recipient = payload.get("recipient")
    message = payload.get("message")

    # Simulated notification (email / Slack / SNS etc.)
    print("📨 NOTIFICATION SENT")
    print(f"Event     : {event}")
    print(f"Recipient : {recipient}")
    print(f"Message   : {message}")

    return json.dumps({"status": "sent"})

