from contextlib import asynccontextmanager
from fastapi import (
    FastAPI,
)
from fastapi.responses import RedirectResponse
import pytz
from src.exports_api import exports_router
from src.pdf_api import pdf_router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.scheduled_tasks import clean_unused_files

load_dotenv()

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        clean_unused_files,
        CronTrigger(hour=19, minute=0, timezone=pytz.UTC),
        id="daily_clean_unused_files",
        name="Cleanup of unused files daily at 19:00 UTC",
    )
    scheduler.start()

    yield  # This is where FastAPI runs

    scheduler.shutdown()


app = FastAPI(lifespan=lifespan, title="PDF tables processing API")


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url="/docs")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:8080",  # Vue default
        "http://127.0.0.1:5173",  # Vite default
        "http://localhost:5173",  # Vite alternative
        "http://127.0.0.1:8000",
        "https://pdf-table-extractor.dyn.cloud.e-infra.cz",
        "https://api.pdf-table-extractor.dyn.cloud.e-infra.cz",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf_router)
app.include_router(exports_router)
