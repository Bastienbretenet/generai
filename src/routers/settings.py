from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from storage.config_store import get_setting, set_setting
from config import HASH_METHODS, UUID_METHODS, API_PROVIDERS, DB_TYPES

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/settings", response_class=HTMLResponse)
async def setting(request: Request):
    saved = {
        "db_type": get_setting("db_type", "postgresql"),
        "db_host": get_setting("db_host", "localhost"),
        "db_port": get_setting("db_port", "5432"),
        "db_name": get_setting("db_name", ""),
        "db_user": get_setting("db_user", ""),
        "db_password": get_setting("db_password", ""),
        "hash_method": get_setting("hash_method", "bcrypt"),
        "uuid_method": get_setting("uuid_method", "uuid7"),
        "password": get_setting("password", ""),
        "provider": get_setting("provider", ""),
        **{provider["name"]: get_setting(f"api_key_{provider['name']}", "") for provider in API_PROVIDERS.values()},
        **{f"{provider['name']}_model": get_setting(f"{provider['name']}_model", next(iter(provider["models"]))) for provider in API_PROVIDERS.values()}
    }
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "db_types": DB_TYPES,
            "hash_methods": HASH_METHODS,
            "uuid_methods": UUID_METHODS,
            "api_providers": API_PROVIDERS,
            "saved": saved
        }
    )

@router.post("/settings/save")
async def settings_save(request: Request):
    form = await request.form()
    for db_key in ("db_type", "db_host", "db_port", "db_name", "db_user", "db_password"):
        value = form.get(db_key)
        if value:
            set_setting(db_key, value)
    hash_method = form.get("hash_method")
    if hash_method:
        set_setting("hash_method", hash_method)
    uuid_method = form.get("uuid_method")
    if uuid_method:
        set_setting("uuid_method", uuid_method)
    password = form.get("password")
    if password:
        set_setting("password", password)
    provider_choice = form.get("provider")
    if provider_choice:
        set_setting("provider", provider_choice)
    for key, provider in API_PROVIDERS.items():
        api_key = form.get(provider["name"])
        set_setting(f"api_key_{provider['name']}", api_key)
        model = form.get(f"{provider['name']}_model")
        set_setting(f"{provider['name']}_model", model)

    return HTMLResponse("✅ Sauvegardé")

@router.get("/settings/test-db", response_class=HTMLResponse)
async def test_db_badge(request: Request):
    db_type = get_setting("db_type", "postgresql")
    try:
        from storage.target_db import get_engine
        from sqlalchemy import text
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return HTMLResponse(
            f'<div class="recap-item recap-item--ok">'
            f'<span class="recap-label">DB</span>'
            f'<span class="recap-value">{db_type}</span>'
            f'</div>'
        )
    except Exception:
        return HTMLResponse('<div class="recap-item recap-item--error"><span class="recap-label">DB</span><span class="recap-value">Erreur</span></div>')

@router.post("/settings/test-db", response_class=HTMLResponse)
async def test_db(request: Request):
    from sqlalchemy import create_engine, text
    from storage.target_db import build_url
    try:
        form = await request.form()
        db_type = form.get("db_type", "postgresql")
        host = form.get("db_host", "localhost")
        port = form.get("db_port", "5432")
        name = form.get("db_name", "")
        user = form.get("db_user", "")
        password = form.get("db_password", "")
        url = build_url(db_type, host, port, name, user, password)
        with create_engine(url).connect() as conn:
            conn.execute(text("SELECT 1"))
        return HTMLResponse('<span class="test-ok">✅ Connexion réussie</span>')
    except Exception as e:
        return HTMLResponse(f'<span class="test-error">❌ {e}</span>')
