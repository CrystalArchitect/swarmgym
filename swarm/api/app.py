"""SwarmGym Web API — FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from swarm.api.routers import auditor


def create_app() -> FastAPI:
    """Create the SwarmGym FastAPI application."""
    app = FastAPI(
        title="SwarmGym API",
        description=(
            "On-chain safety auditor for multi-agent AI systems. "
            "Computes distributional safety metrics and attests results on Base."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    app.include_router(auditor.router, prefix="/api/v1/audits", tags=["audits"])

    return app


app = create_app()
