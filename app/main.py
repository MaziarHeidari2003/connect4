from fastapi import FastAPI
from app.core.config import settings
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from app.api.api_v1.api import api_router


app = FastAPI(title=settings.PROJECT_NAME)
if settings.DEBUG:
    app.openapi_url = f"{settings.API_V1_STR}"
    app.setup()
if settings.SUB_PATH:
    app.mount(f"{settings.SUB_PATH}", app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


app.include_router(api_router, prefix=settings.API_V1_STR)


def custom_open_api():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Connect4 Docs",
        version="",
        routes=app.routes,
        servers=[{"url": settings.SUB_PATH if settings.SUB_PATH else ""}],
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema
