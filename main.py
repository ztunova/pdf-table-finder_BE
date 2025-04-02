from fastapi import (
    FastAPI,
)
from fastapi.responses import RedirectResponse
from src.exports_api import exports_router
from src.pdf_api import pdf_router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="PDF tables processing API")


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
