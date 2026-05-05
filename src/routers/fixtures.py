from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from services.orchestrator import fixture_stream
from storage.target_db import apply_sql
from storage.config_store import add_history, get_setting, set_setting
from config import API_PROVIDERS

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    hash_method = get_setting("hash_method", "bcrypt")
    provider_choice = get_setting("provider", "")
    active_provider = None
    for provider in API_PROVIDERS.values():
        api_key = get_setting(f"api_key_{provider['name']}", "")
        if api_key and (provider["name"] == provider_choice or not provider_choice):
            model_key = get_setting(f"{provider['name']}_model", next(iter(provider["models"])))
            active_provider = {
                "label": provider["label"],
                "model_label": provider["models"].get(model_key, model_key),
            }
            break
    project_context = get_setting("project_context", "")
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "has_api_key": bool(active_provider),
            "hash_method": hash_method,
            "active_provider": active_provider,
            "project_context": project_context,
        }
    )

@router.post("/save-context")
async def save_context(request: Request):
    form = await request.form()
    context = form.get("project_context", "")
    set_setting("project_context", context)
    return HTMLResponse("")

@router.post("/ask")
async def ask_route(request: Request):
    form = await request.form()
    user_request = form.get("value", "")
    hash_method = form.get("hash_method", "bcrypt")
    return StreamingResponse(
        fixture_stream(user_request, hash_method),
        media_type="text/event-stream"
    )

@router.post("/apply")
async def apply(request: Request):
    import json
    form = await request.form()
    sql = form.get("sql", "")
    prompt = form.get("prompt", "")
    steps_raw = form.get("steps", "[]")
    try:
        steps = json.loads(steps_raw)
    except Exception:
        steps = []
    try:
        apply_sql(sql)
        if prompt:
            add_history(prompt, steps, sql)
        return HTMLResponse("<p>✅ Fixtures appliquées avec succès</p>")
    except Exception as e:
        return HTMLResponse(f"<p>❌ Erreur : {e}</p>")
