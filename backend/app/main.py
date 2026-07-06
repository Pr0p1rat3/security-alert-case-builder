from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    alerts,
    audit,
    auth,
    cases,
    dashboard,
    evidence,
    iocs,
    mitre,
    notes,
    reports,
    search,
    tasks,
    timeline,
    users,
)
from app.core.config import get_settings
from app.db.seed import seed_initial_data
from app.db.session import SessionLocal, engine
from app.models.base import Base


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        if settings.environment == "development":
            raise exc
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(cases.router)
    app.include_router(alerts.router)
    app.include_router(iocs.router)
    app.include_router(timeline.router)
    app.include_router(mitre.router)
    app.include_router(tasks.router)
    app.include_router(notes.router)
    app.include_router(evidence.router)
    app.include_router(reports.router)
    app.include_router(audit.router)
    app.include_router(dashboard.router)
    app.include_router(search.router)

    @app.on_event("startup")
    def startup() -> None:
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            seed_initial_data(db)
        settings.evidence_storage_path.mkdir(parents=True, exist_ok=True)

    return app


app = create_app()
