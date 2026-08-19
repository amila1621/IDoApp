

import json
import os

from anthropic import Anthropic
from app.llm.prompt import SYSTEM_PROMPT, EXAMPLES

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")

class LLMError(Exception):
    """ Raised when the LLM call fails for any reason. """


def available() -> bool:
    """ True if API key is configured and LLM is available. """
    return bool(os.getenv("ANTHROPIC_API_KEY"))

def complete(text: str) -> str:
    """Send the task text to claude return the row JSON string with the enrichment data. Raise LLMError if the call fails for any reason so callers can fall back."""
    try:
        client = Anthropic()
        response = client.messages.create(
            model=MODEL,
            max_tokens=300,
            temperature=0.2,
            system=SYSTEM_PROMPT,
            messages= [
                *EXAMPLES,
                {"role": "user", "content": text}
            ]
        )
        return response.content[0].text
    except Exception as e:
        raise LLMError(str(e)) from e

def strip_fences(row: str) -> str:
    """ Remove ''' json fences from the LLM output if they exist. """
    cleaned = row.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    return cleaned.strip()


