from storage.target_db import get_schema
from services.llm import ask
from services.prompt_loader import prompt_extract_relevant_tables, prompt_generate_fixtures
from services.replacers import SQLReplacer
from storage.config_store import get_setting
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import asyncio
import base64
import json

env = Environment(loader=FileSystemLoader(Path(__file__).parent.parent / "templates"))

async def fixture_stream(user_request: str, hash_method: str):
    steps = []
    project_context = get_setting("project_context", "")

    step = "⏳ Récupération du schéma..."
    steps.append(step)
    yield f"data: {step}\n\n"
    schema = await asyncio.to_thread(get_schema)

    step = "🔍 Identification des tables nécessaires..."
    steps.append(step)
    yield f"data: {step}\n\n"
    prompt1 = prompt_extract_relevant_tables(schema, user_request)
    relevant_tables = await asyncio.to_thread(ask, prompt1)
    step = f"✅ Tables identifiées : {', '.join(relevant_tables)}"
    steps.append(step)
    yield f"data: {step}\n\n"

    filtered_schema = {t: schema[t] for t in relevant_tables if t in schema}

    step = "🤖 Génération des fixtures..."
    steps.append(step)
    yield f"data: {step}\n\n"
    prompt2 = prompt_generate_fixtures(filtered_schema, user_request, project_context)
    fixtures = await asyncio.to_thread(ask, prompt2)

    step = "🔐 Remplacement des UUIDs et passwords..."
    steps.append(step)
    yield f"data: {step}\n\n"
    uuid_method = get_setting("uuid_method", "uuid7")
    sql = SQLReplacer(fixtures).replace_uuids(uuid_method).replace_passwords(hash_method).get()

    template = env.get_template("partials/result.html")
    html = template.render(sql=sql, prompt=user_request, steps=json.dumps(steps))
    html_b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")

    yield f"data: DONE:{html_b64}\n\n"
