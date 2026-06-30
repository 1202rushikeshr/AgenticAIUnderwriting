from crewai import LLM

def get_underwriting_llm():
    return LLM(
        model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
        temperature=0.2,
        max_tokens=1024,
        region_name="us-east-1"
    )

underwriting_llm = get_underwriting_llm()
