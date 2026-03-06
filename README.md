# project-fast-api

一个最小可运行的 FastAPI 项目模板，包含：

- 环境配置加载（`config/.env.*`）
- 统一返回结构（`Result`）
- 文件+控制台日志（按天切分）
- Docker 构建与一键部署脚本（`deploy.sh`）

## 技术栈

- Python 3.12
- FastAPI 0.121.2
- Uvicorn 0.38.0
- Pydantic 2.12.4

## 项目结构

```text
.
├── api/                # 路由
├── bean/               # 返回模型等基础对象
├── config/             # 环境配置与 settings
├── core/               # 日志等核心模块
├── util/               # 工具函数
├── main.py             # 应用入口
├── requirements.t      # Python 依赖（注意文件名是 requirements.t）
├── Dockerfile
└── deploy.sh
```

## 环境配置

项目通过环境变量 `CONFIG_FILE_PATH` 指定配置文件，默认值为 `.env.dev`。

加载逻辑：

- `CONFIG_FILE_PATH=.env.dev` -> 读取 `config/.env.dev`
- `CONFIG_FILE_PATH=.env.prod` -> 读取 `config/.env.prod`

示例（`config/.env.dev`）：

```env
SERVICE_PORT=7001
LOG_PATH="~/code/config/log/test/dev"
LOG_NAME="analyse_log"
```

## 本地运行

### 1. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.t
```

### 2. 启动服务

默认使用 `config/.env.dev`：

```bash
python main.py
```

或显式指定配置文件：

```bash
CONFIG_FILE_PATH=.env.prod python main.py
```

## 接口文档

启动后访问：

- Swagger UI: `http://127.0.0.1:<SERVICE_PORT>/docs`
- ReDoc: `http://127.0.0.1:<SERVICE_PORT>/redoc`

## 示例接口

当前项目包含一个测试接口：

- Method: `GET`
- Path: `/apitest`
- Query: `profile_id`, `page_type`

请求示例：

```bash
curl "http://127.0.0.1:7001/apitest?profile_id=1001&page_type=home"
```

返回示例：

```json
{
  "success": true,
  "message": "操作成功！",
  "code": 200,
  "result": {
    "profile_id": "1001",
    "page_type": "home"
  },
  "timestamp": 1710000000000
}
```

## Docker 运行

### 构建镜像

```bash
docker build -t test .
```

### 运行容器

```bash
docker run -d \
  --name test \
  -p 8001:8001 \
  -e CONFIG_FILE_PATH=.env.prod \
  -v "$(pwd)/config/.env.prod:/app/config/.env.prod" \
  -v "$(pwd)/logs:/app/logs" \
  test
```

## 使用 deploy.sh 一键部署

`deploy.sh` 默认会：

1. 删除旧容器 `test`
2. 删除旧镜像 `test`
3. 重新构建镜像
4. 挂载配置与日志目录并启动容器

执行前可按需修改脚本顶部变量：

- `IMAGE_NAME`
- `CONTAINER_NAME`
- `CONFIG_FILE_PATH`
- `HOST_PORT`
- `CONTAINER_LOG_PATH`

执行：

```bash
bash deploy.sh
```

## 日志说明

日志初始化在 `main.py` 中执行：`setup_logging()`。

- 输出位置由 `LOG_PATH` 控制
- 文件名由 `LOG_NAME` 控制
- 按天滚动，保留 14 天

## 注意事项

- 当前依赖文件名是 `requirements.t`（不是常见的 `requirements.txt`）。
- 当前路由写法为 `@router.get("test")`，因此路径是 `/apitest`。
  - 若期望路径为 `/api/test`，可改为 `@router.get("/test")`。
