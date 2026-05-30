import psycopg
import redis
from qdrant_client import QdrantClient
from app.core.config import settings

def check_postgres():
    try:
        with psycopg.connect(settings.postgres_dsn, connect_timeout=3) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        return {"ok": True, "message": "PostgreSQL connection successful"}
    except Exception as error:
        return {"ok": False, "message": str(error)}

def check_redis():
    try:
        client = redis.Redis(host=settings.redis_host, port=settings.redis_port, socket_connect_timeout=3)
        client.ping()
        return {"ok": True, "message": "Redis connection successful"}
    except Exception as error:
        return {"ok": False, "message": str(error)}

def check_qdrant():
    try:
        client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port, timeout=3)
        client.get_collections()
        return {"ok": True, "message": "Qdrant connection successful"}
    except Exception as error:
        return {"ok": False, "message": str(error)}