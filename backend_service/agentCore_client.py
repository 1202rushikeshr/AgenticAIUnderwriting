# agentCore_client.py
import boto3
import json
import uuid

client = boto3.client(
    "bedrock-agentcore",
    region_name="us-east-1"
)

AGENT_RUNTIME_ARN = (
    "arn:aws:bedrock-agentcore:us-east-1:"
    "241474165033:runtime/AWS_Underwriting_Agent-AG0kahFd5D"
)

def invoke_underwriting_agent(payload: dict):
    """
    Invokes Amazon Bedrock AgentCore Runtime
    """
    session_id = f"session-{uuid.uuid4()}"  # MUST be >= 33 chars

    response = client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_RUNTIME_ARN,
        runtimeSessionId=session_id,
        payload=json.dumps(payload),
        qualifier="DEFAULT"  # uses DEFAULT endpoint
    )

    result_bytes = response["response"].read()
    return json.loads(result_bytes)
