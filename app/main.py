import logging
from contextlib import asynccontextmanager

# from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import asyncpg
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .admin_panel import admin_panel_apply, authentication_backend
from .config import settings
from .database import engine
from .services.redis_service import get_redis, get_cache
from .utils.middlewares import handle_integrity_errors
from .user import routes as user_route
from .chat import routes as chat_route
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
# from debug_toolbar.middleware import DebugToolbarMiddleware
from sqladmin import Admin

@asynccontextmanager
async def lifespan(_app: FastAPI):
    _app.redis = await get_redis()

    _postgres_dsn = settings.postgres_url.unicode_string()

    try:

        redis_cache = await get_cache()
        FastAPICache.init(RedisBackend(redis_cache), prefix="fastapi-cache")

        _app.postgres_pool = await asyncpg.create_pool(
            dsn = _postgres_dsn,
            # min_size=20,  # Higher minimum size to quickly handle many concurrent connections
            # max_size=100,  # Larger maximum size to support peak loads
            # max_inactive_connection_lifetime=300,  # Recycle idle connections after 5 minutes
            # timeout=60,
        )
        # await init_models()

        yield

    finally:
        await _app.redis.close()
        await _app.postgres_pool.close()

app = FastAPI(lifespan=lifespan, debug=True)
# app.add_middleware(
#     DebugToolbarMiddleware,
#     panels=["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"],
#     profiler_options={'interval': .0002}
# )
app.add_middleware(BaseHTTPMiddleware, dispatch=handle_integrity_errors)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

app.include_router(user_route.router)
app.include_router(chat_route.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def chat(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)

admin_panel_apply(admin)
