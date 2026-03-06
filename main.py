# main.py

import uvicorn
from fastapi import FastAPI

from api.api_test import router as test_router
from config.settings import SERVICE_PORT
from core.log import setup_logging

def create_app() -> FastAPI: 
	app = FastAPI(title="Aesthetic Customer Value Engine")

	
	app.include_router(test_router, prefix="/api", tags=["test"])

	return app


app = create_app()
setup_logging()  # 初始化日志


if __name__ == "__main__": 
	# uvicorn.run(
	# 	"main:app",
	# 	host="0.0.0.0",
	# 	port=8001, # lsof -i: $port|awk '{if(NR>=2) print $2}'|xargs kill
	# 	# reload=True, # 目录里的文件有改动,就自动重启服务。
	# 	# log_level="debug",
	# )
	config = uvicorn.Config(
		"main:app",
		host="0.0.0.0",
		port=SERVICE_PORT,
		log_config=None, # 🔥 关键：禁止 uvicorn 覆盖 logging
		access_log=True,  # 可选：确保 access log 打开
	)
	server = uvicorn.Server(config)
	import asyncio
	
	asyncio.get_event_loop().run_until_complete(server.serve())
	