import os

from core.util.env_util import load_env

CONFIG_FILE_PATH = os.getenv("CONFIG_FILE_PATH", ".env.dev")
print(
    f"ENV_PATH: {CONFIG_FILE_PATH}"
)  # logging配置引用了本文件， 本文件优先级最高，所以使用print
env = load_env(CONFIG_FILE_PATH)

SERVICE_PORT = env.get("SERVICE_PORT")

LOG_PATH = env.get("LOG_PATH")
LOG_NAME = os.getenv("LOG_NAME")

POSTGRES_URL = env.get("POSTGRES_URL")
POSTGRES_PORT = env.get("POSTGRES_PORT", 5432)
POSTGRES_DATABASE = env.get("POSTGRES_DATABASE", "test")
POSTGRES_USERNAME = env.get("POSTGRES_USERNAME", "postgres")
POSTGRES_PASSWORD = env.get("POSTGRES_PASSWORD", "postgres")


OLLAMA_CHAT_URL = env.get("OLLAMA_CHAT_URL", "http://127.0.0.1:11434/api/chat")
OLLAMA_GENERATE_URL = env.get(
    "OLLAMA_GENERATE_URL", "http://127.0.0.1:11434/api/generate"
)