import json
import anthropic
import openai
from mistralai.client import Mistral
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
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse(message.content[0].text)

def _ask_openai(prompt: str, api_key: str):
    model = get_setting("chatgpt_model", "gpt-4o-mini")
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse(response.choices[0].message.content)

def _ask_mistral(prompt: str, api_key: str):
    model = get_setting("mistral_model", "mistral-small-latest")
    client = Mistral(api_key=api_key)
    response = client.chat.complete(
        model=model,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse(response.choices[0].message.content)

def _ask_openrouter(prompt: str, api_key: str):
    model = get_setting("openrouter_model", "meta-llama/llama-3.3-70b-instruct")
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )
    response = client.chat.completions.create(
        model=model,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse(response.choices[0].message.content)

def ask(prompt: str):
    claude_key = get_setting("api_key_claude")
    openai_key = get_setting("api_key_chatgpt")
    mistral_key = get_setting("api_key_mistral")
    openrouter_key = get_setting("api_key_openrouter")
    provider = get_setting("provider", "")

    if provider == "claude" and claude_key:
        return _ask_claude(prompt, claude_key)
    if provider == "chatgpt" and openai_key:
        return _ask_openai(prompt, openai_key)
    if provider == "mistral" and mistral_key:
        return _ask_mistral(prompt, mistral_key)
    if provider == "openrouter" and openrouter_key:
        return _ask_openrouter(prompt, openrouter_key)

    if claude_key:
        return _ask_claude(prompt, claude_key)
    if openai_key:
        return _ask_openai(prompt, openai_key)
    if mistral_key:
        return _ask_mistral(prompt, mistral_key)
    if openrouter_key:
        return _ask_openrouter(prompt, openrouter_key)

    raise ValueError("Aucune clé API configurée. Ajoutez une clé dans Settings.")
