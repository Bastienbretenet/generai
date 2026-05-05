from storage.target_db import get_schema, get_protected_table_ids
from services.llm import ask
from services.prompt_loader import prompt_extract_relevant_tables, prompt_generate_fixtures, prompt_fix_fixtures
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

    protected_raw = get_setting("protected_tables", "[]")
    try:
        import json as _json
        protected_tables = _json.loads(protected_raw)
    except Exception:
        protected_tables = []

    step = "🔍 Identification des tables nécessaires..."
    steps.append(step)
    yield f"data: {step}\n\n"
    prompt1 = prompt_extract_relevant_tables(schema, user_request)
    relevant_tables = await asyncio.to_thread(ask, prompt1)
    step = f"✅ Tables identifiées : {', '.join(relevant_tables)}"
    steps.append(step)
    yield f"data: {step}\n\n"

    filtered_schema = {t: schema[t] for t in relevant_tables if t in schema and t not in protected_tables}

    protected_data = None
    if protected_tables:
        protected_data = await asyncio.to_thread(get_protected_table_ids, protected_tables)

    step = "🤖 Génération des fixtures..."
    steps.append(step)
    yield f"data: {step}\n\n"
    prompt2 = prompt_generate_fixtures(filtered_schema, user_request, project_context, protected_data)
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

async def fix_stream(user_request: str, sql: str, error: str, hash_method: str):
    steps = []
    project_context = get_setting("project_context", "")

    step = "🔧 Correction du SQL en cours..."
    steps.append(step)
    yield f"data: {step}\n\n"
    prompt = prompt_fix_fixtures(user_request, sql, error, project_context)
    fixed_sql_raw = await asyncio.to_thread(ask, prompt)

    step = "🔐 Remplacement des UUIDs et passwords..."
    steps.append(step)
    yield f"data: {step}\n\n"
    uuid_method = get_setting("uuid_method", "uuid7")
    fixed_sql = SQLReplacer(fixed_sql_raw).replace_uuids(uuid_method).replace_passwords(hash_method).get()

    template = env.get_template("partials/result.html")
    html = template.render(sql=fixed_sql, prompt=user_request, steps=json.dumps(steps))
    html_b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")

    yield f"data: DONE:{html_b64}\n\n"
