import json
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from storage.config_store import get_setting, set_setting
from storage.target_db import get_schema

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/tables", response_class=HTMLResponse)
async def tables_page(request: Request):
    try:
        schema = get_schema()
        table_names = list(schema.keys())
    except Exception:
        table_names = []

    protected_raw = get_setting("protected_tables", "[]")
    try:
        protected = json.loads(protected_raw)
    except Exception:
        protected = []

    return templates.TemplateResponse(
        request=request,
        name="tables.html",
        context={"tables": table_names, "protected": protected},
    )


@router.post("/tables/save", response_class=HTMLResponse)
async def tables_save(request: Request):
    form = await request.form()
    protected = form.getlist("protected_tables")
    set_setting("protected_tables", json.dumps(protected))
    return HTMLResponse("✅ Sauvegardé")
