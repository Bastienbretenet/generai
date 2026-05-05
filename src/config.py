DB_TYPES = {
    "postgresql": {"label": "PostgreSQL", "default_port": "5432"},
    "mysql": {"label": "MySQL", "default_port": "3306"},
}

UUID_METHODS = {
    "uuid7": {"label": "UUID v7 (time-ordered)"},
    "uuid6": {"label": "UUID v6 (time-ordered)"},
    "uuid5": {"label": "UUID v5 (name-based, SHA-1)"},
}

HASH_METHODS = {
    "bcrypt": {
        "label": "bcrypt",
    },
    "argon2": {
        "label": "Argon2",
    },
    "sha256": {
        "label": "SHA-256",
    },
}

API_PROVIDERS = {
    "Anthropic": {
        "label": "Claude",
        "name": "claude",
        "placeholder": "sk-ant-api03...",
        "lien": "https://platform.claude.com/",
        "models" : {
            "claude-haiku-4-5-20251001": "Haiku (rapide, économique)",
            "claude-sonnet-4-6": "Sonnet (équilibré)",
            "claude-opus-4-7": "Opus (qualité maximale)"
        }
    },
    "OpenAi": {
        "label": "ChatGpt",
        "name": "chatgpt",
        "placeholder": "sk-proj-...",
        "lien": "https://platform.openai.com/",
        "models" : {
            "gpt-4o-mini": "GPT Mini",
            "gpt-5.4-nano": "GPT-5.4 Nano (économique)",
            "gpt-5.4-mini": "GPT-5.4 Mini (équilibré)",
            "gpt-5.5": "GPT-5.5 (qualité maximale)",
        }
    },
    "Mistral": {
        "label": "Mistral AI",
        "name": "mistral",
        "placeholder": "...",
        "lien": "https://console.mistral.ai/",
        "models": {
            "mistral-small-latest": "Mistral Small (rapide, économique)",
            "mistral-medium-latest": "Mistral Medium (équilibré)",
            "mistral-large-latest": "Mistral Large (qualité maximale)",
            "codestral-latest": "Codestral (spécialisé code)",
        }
    },
    "OpenRouter": {
        "label": "OpenRouter",
        "name": "openrouter",
        "placeholder": "sk-or-v1-...",
        "lien": "https://openrouter.ai/",
        "models": {
            "meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B (économique)",
            "google/gemini-2.0-flash-001": "Gemini 2.0 Flash (rapide)",
            "deepseek/deepseek-chat-v3-0324": "DeepSeek V3 (équilibré)",
            "anthropic/claude-sonnet-4-6": "Claude Sonnet via OpenRouter",
        }
    },
}