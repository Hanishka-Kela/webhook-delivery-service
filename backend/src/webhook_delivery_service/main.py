from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from webhook_delivery_service.api.routes.health import router as health_router
from webhook_delivery_service.infrastructure.config.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=False,
    )

    app.include_router(health_router)

    return app


app = create_app()
