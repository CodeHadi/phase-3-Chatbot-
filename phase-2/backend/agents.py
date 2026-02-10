import os
import json
from typing import Any, Dict, List, Optional

try:
    import openai
except Exception:
    openai = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


SYSTEM_PROMPT = (
    "You are an assistant that translates user messages into a small set of allowed MCP tool calls or a plain reply. "
    "Return JSON only. Format: {\"reply\": string|null, \"actions\": [{\"tool\":string, \"input\":{...}}]}"
)


def call_model_for_actions(user_message: str, examples: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Call OpenAI chat completion to get structured JSON actions or reply.

    This is a thin adapter; in production use the official Agents SDK.
    """
    if not openai or not OPENAI_API_KEY:
        # Fallback: naive heuristic — if message contains 'add' create a todo
        if "add" in user_message.lower() or "create" in user_message.lower():
            title = user_message.strip()
            return {"reply": "I've created the task.", "actions": [{"tool": "todo.add", "input": {"title": title}}]}
        return {"reply": "I understood you.", "actions": []}

    prompt = []
    prompt.append({"role": "system", "content": SYSTEM_PROMPT})
    if examples:
        for ex in examples:
            prompt.append({"role": "user", "content": ex.get("user", "")})
            prompt.append({"role": "assistant", "content": ex.get("assistant", "")})
    prompt.append({"role": "user", "content": user_message})

    try:
        resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=prompt, max_tokens=400)
        text = resp.choices[0].message.content
        # Parse JSON from model output
        payload_text = text.strip()
        # Try to extract first JSON object
        try:
            data = json.loads(payload_text)
        except Exception:
            # Try to find JSON substring
            start = payload_text.find("{")
            end = payload_text.rfind("}")
            if start != -1 and end != -1:
                data = json.loads(payload_text[start:end+1])
            else:
                return {"reply": payload_text, "actions": []}
        # Ensure keys
        return {"reply": data.get("reply"), "actions": data.get("actions", [])}
    except Exception as e:
        return {"reply": f"Model error: {str(e)}", "actions": []}
