from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from storage.config_store import get_history, get_history_item

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    items = get_history()
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={"items": items}
    )

@router.get("/history/{item_id}", response_class=HTMLResponse)
async def history_detail(request: Request, item_id: int):
    item = get_history_item(item_id)
    if not item:
        return HTMLResponse("Not found", status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={"items": get_history(), "selected": item}
    )
