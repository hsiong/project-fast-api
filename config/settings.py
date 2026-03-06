import os

from util.env_util import load_env

CONFIG_FILE_PATH = os.getenv("CONFIG_FILE_PATH", ".env.dev")
print(f"ENV_PATH: {CONFIG_FILE_PATH}") # logging配置引用了本文件， 本文件优先级最高，所以使用print
env = load_env(CONFIG_FILE_PATH)

SERVICE_PORT = env.get('SERVICE_PORT')

LOG_PATH = env.get('LOG_PATH')
LOG_NAME = env.get('LOG_NAME')
