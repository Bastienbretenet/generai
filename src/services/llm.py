import json
import anthropic
import openai
from storage.config_store import get_setting

def _parse(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text

def _ask_claude(prompt: str, api_key: str):
    model = get_setting("claude_model", "claude-haiku-4-5-20251001")
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse(message.content[0].text)

def _ask_openai(prompt: str, api_key: str):
    model = get_setting("chatgpt_model", "gpt-4o-mini")
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse(response.choices[0].message.content)

def ask(prompt: str):
    claude_key = get_setting("api_key_claude")
    openai_key = get_setting("api_key_chatgpt")
    provider = get_setting("provider", "")

    if provider == "claude" and claude_key:
        return _ask_claude(prompt, claude_key)
    if provider == "chatgpt" and openai_key:
        return _ask_openai(prompt, openai_key)

    if claude_key:
        return _ask_claude(prompt, claude_key)
    if openai_key:
        return _ask_openai(prompt, openai_key)

    raise ValueError("Aucune clé API configurée. Ajoutez une clé dans Settings.")
