import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = OpenAI(model=MODEL, openai_api_key=OPENAI_API_KEY, temperature=0.0, max_tokens=1000)

PROMPT = """
You are a follow-up assistant. For the input message, determine whether a follow-up or reminder is required.
If yes, extract the follow-up as JSON with these fields:
- task: short description of the follow-up action
- due_date: explicit date if provided (YYYY-MM-DD), or a natural expression (e.g., "next Monday", "in 2 days", or empty if unknown)
- type: one of ["one-time", "recurring", "waiting", "info"]
- trigger: (optional) what should trigger the follow-up (e.g., "client feedback received")
- urgency: low/medium/high (based on phrasing)
Output strictly valid JSON ONLY. Example:
{{"follow_up_required": true, "task": "Send project report", "due_date":"2025-10-20", "type":"one-time", "trigger":"", "urgency":"high"}}

Message:
\"\"\"{message}\"\"\"
"""

prompt = PromptTemplate(input_variables=["message"], template=PROMPT)
chain = LLMChain(llm=llm, prompt=prompt)

def parse_message(message):
    response = chain.run(message=message)
    try:
        # sometimes the model returns newlines; try to extract JSON
        obj = json.loads(response.strip())
    except Exception:
        # fallback: try to find JSON substring
        import re
        m = re.search(r'(\{.*\})', response, re.S)
        if not m:
            raise ValueError("LLM did not return JSON: " + response)
        obj = json.loads(m.group(1))
    # Add metadata
    obj['source_text'] = message
    obj['created_at'] = datetime.now(datetime.UTC).isoformat()
    return obj