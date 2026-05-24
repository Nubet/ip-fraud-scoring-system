from fastapi import FastAPI

from app.adapters.api.router import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="IP Fraud Scoring System",
        version="0.1.0",
        description="API for evaluating IP fraud risk.",
    )
    app.include_router(api_router)
    return app


app = create_app()
