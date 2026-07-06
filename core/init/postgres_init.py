from fastapi import FastAPI
import logging

from core.config.settings import (
    POSTGRES_DATABASE,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_URL,
    POSTGRES_USERNAME,
)



def init_postgres(app: FastAPI) -> None:
    app.postgresSession = None
    if not POSTGRES_URL:
        return

    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import URL
    from sqlalchemy.orm import scoped_session, sessionmaker

    postgres_url = URL.create(
        drivername="postgresql+psycopg2",
        username=POSTGRES_USERNAME,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_URL,
        port=POSTGRES_PORT,
        database=POSTGRES_DATABASE,
    )
    engine = create_engine(postgres_url, pool_pre_ping=True)
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        logging.info(f"Connected to PostgreSQL at {POSTGRES_URL}")
        
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    app.postgresSession = scoped_session(session_factory)

    @app.middleware("http")
    async def postgres_session_middleware(request, call_next):
        try:
            response = await call_next(request)
            app.postgresSession.commit()
            return response
        except Exception:
            app.postgresSession.rollback()
            raise
        finally:
            app.postgresSession.remove()
