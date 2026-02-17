from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import check_db_connection

from app.routers.auth import router as auth_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    # CORS (для фронта в ЛВС / минимального внешнего доступа)
    origins = settings.cors_origins_list()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins != ["*"] else ["*"],
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    def health() -> dict:
        # проверка БД включена (быстро покажет проблемы с подключением)
        check_db_connection()
        return {"status": "ok"}

    # Далее подключаем роутеры (пока заглушки)
    # from app.routers import books, auth, reservations, loans, notifications, admin
    # app.include_router(auth.router, prefix=settings.api_prefix)
    # app.include_router(books.router, prefix=settings.api_prefix)
    # ...

    return app


app = create_app()
app.include_router(auth_router, prefix=settings.api_prefix)