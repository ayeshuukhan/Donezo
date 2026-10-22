from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.routes import router as tasks_router

app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    description="Small REST service for managing tasks (CRUD, validation, tests, Docker).",
)

app.include_router(tasks_router)


@app.get("/", include_in_schema=False)
def root():
    # "/" kholne par seedha Swagger UI (/docs) par bhej do
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}