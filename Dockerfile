# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and buffer stdout/err
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN python -m venv /opt/venv


FROM base AS packages

# ===== 环境变量：让 apt / uv / pip 都走代理 & 国内源 =====
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG http_proxy
ARG https_proxy
# uv 的国内源
ARG UV_INDEX_URL
# pip 的国内源（备用）
ARG PIP_INDEX_URL
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV http_proxy=${http_proxy}
ENV https_proxy=${https_proxy}
ENV UV_INDEX_URL=${UV_INDEX_URL}
ENV PIP_INDEX_URL=${PIP_INDEX_URL}
RUN sed -i 's@deb.debian.org@mirrors.aliyun.com@g' /etc/apt/sources.list.d/debian.sources

# 安装编译依赖 (仅在构建阶段存在)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
    
COPY requirements.t requirements.t

# 安装运行依赖。requirements.t 不变时，这一层会被 Docker 缓存复用。
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.t

# 瘦身
FROM base AS production

# 复制 packages 阶段生成的虚拟环境，最终镜像不包含编译器。
COPY --from=packages /opt/venv /opt/venv

# Copy application source
COPY . .

# Create default writable paths expected by the app
RUN mkdir -p /app/logs

# 与 CONFIG_FILE_PATH - SERVICE_PORT 保持一致
EXPOSE 8001

# 共用网络, 让宿主机 app的proxy协议 决定是否代理
ENV http_proxy=""
ENV https_proxy=""
ENV all_proxy=""
ENV HTTP_PROXY=""
ENV HTTPS_PROXY=""
ENV ALL_PROXY=""

CMD ["python", "main.py"]
# CMD ["tail", "-f", "/dev/null"]
