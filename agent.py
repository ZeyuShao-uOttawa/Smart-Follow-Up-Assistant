import os
import json
import re
from datetime import datetime, timezone
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model=MODEL, openai_api_key=OPENAI_API_KEY, max_tokens=10000)

PROMPT = """
You are a personal assistant. For the input message, determine whether the tasks need a follow-up, is a ongoing task, or if the taks does not need a follow up.
If a message contains a action, it is likely that a follow-up is required or it is a ongoing task. Only if the task is purely informational, then it doesn't require a follow-up nor is it considered ongoing.
Extract the following information from the message as a JSON with these fields:
- status: either follow-up needed, no follow-up needed, or ongoing (If no follow-up needed there will be no followup_date)
- action: determine what action to take if a follow-up is needed or if the task is still ongoing (e.g. "Send project report", empty if no follow up needed and it is not an ongoing task, do not include datetime in action)
- followup_date: explicit datetime if provided (YYYY-MM-DDThh:mm:ss), otherwise translate natural expression (e.g., "next Monday", "in 2 days", "this Tuesday") to datetime (YYYY-MM-DDThh:mm:ss) from the current datetime (also if unknown just add a week to the current datetime)
- type: one of ["one-time", "recurring", "waiting", "info"]
- urgency: low/medium/high (based on phrasing)
Output strictly valid JSON ONLY. Examples:
{{"status": "follow-up needed", "action": "Send project report", "followup_date":"2025-10-1T9:00:00", "type":"one-time", "urgency":"high"}}
{{"status": "no follow-up needed", "action": "Recieved report", "followup_date":"", "type":"info", "urgency":"low"}}
{{"status": "ongoing task", "action": "Update to do list weekly", "followup_date":"2025-10-6T00:00:00", "type":"recurring", "urgency":"low"}}
{{"status": "follow-up needed", "action": "Waiting for feedback", "followup_date":"2025-10-15T00:00:00", "type":"waiting", "urgency":"medium"}}

Message:
\"\"\"{message}\"\"\"
"""

prompt = PromptTemplate(input_variables=["message"], template=PROMPT)
chain = prompt | llm

def parse_message(message):
    response = chain.invoke({"message": message})

    try:
        # Sometimes the model returns newlines; try to extract JSON
        obj = json.loads(response.content.strip())
    except Exception:
        # Fallback: try to find JSON substring
        m = re.search(r'(\{.*\})', response.content, re.S)
        if not m:
            raise ValueError("LLM did not return JSON: " + str(response.content))
        obj = json.loads(m.group(1))
    # Add metadata
    obj['source_text'] = message
    obj['created_at'] = datetime.now(timezone.utc).isoformat()
    return obj