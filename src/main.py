from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from storage.config_store import init_db
from routers import settings, fixtures, history

init_db()
app = FastAPI()
app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(fixtures.router)
app.include_router(settings.router)
app.include_router(history.router)
