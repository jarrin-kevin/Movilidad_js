import os

# Configuración para el receptor (graylog u otro)
RECEIVER_HOST = os.getenv("RECEIVER_HOST", "redis")
RECEIVER_PORT = int(os.getenv("RECEIVER_PORT", "12345"))

CONFIG_RECEIVER = {
    "host": RECEIVER_HOST,
    "port": RECEIVER_PORT,
    "redis_url": (
        f"redis://:{os.getenv('REDIS_PASSWORD')}@"
        f"{os.getenv('REDIS_HOST', 'redis')}:"
        f"{os.getenv('REDIS_PORT', '6379')}"
    )
}

