from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import auth, requests, blueprints, sandboxes

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include all routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(requests.router, prefix="/api/v1")
app.include_router(blueprints.router, prefix="/api/v1")
app.include_router(sandboxes.router, prefix="/api/v1")


@app.get("/health/live", tags=["health"])
def liveness():
    return {"status": "ok", "app": settings.app_name}


@app.get("/health/ready", tags=["health"])
def readiness():
    from app.db.session import SessionLocal
    from sqlalchemy import text
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ready", "db": "connected"}
    except Exception as e:
        return {"status": "not ready", "db": str(e)}


@app.get("/", tags=["root"])
def root():
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
        "environment": settings.app_env
    }