# main.py

import uvicorn
from fastapi import FastAPI

from core.api.api_test import router as test_router
from core.config.settings import SERVICE_PORT
from core.init.log import setup_logging
from core.init.postgres_init import init_postgres


def create_app() -> FastAPI:
	app = FastAPI(title="Aesthetic Customer Value Engine")
	
	app.include_router(test_router, prefix="/api", tags=["attendance"])
	# app.include_router(test_router, prefix="/api", tags=["test"])
	
	return app


def init(app: FastAPI) -> None:
	setup_logging()  # 初始化日志
	init_postgres(app)
	
	# from model.repo.attendance_statistics_repo import AttendanceStatisticsRepo
	# from model.service.attendance_statistics_service import AttendanceStatisticsService
	# app.attendanceStatisticsRepo = AttendanceStatisticsRepo(app.postgresSession)
	# app.attendanceStatisticsService = AttendanceStatisticsService(
	# 	app.attendanceStatisticsRepo
	# )


app = create_app()
init(app)

if __name__ == "__main__":
	# uvicorn.run(
	# 	"main:app",
	# 	host="0.0.0.0",
	# 	port=8001, # lsof -i: $port|awk '{if(NR>=2) print $2}'|xargs kill
	# 	# reload=True, # 目录里的文件有改动,就自动重启服务。
	# 	# log_level="debug",
	# )
	config = uvicorn.Config(
		"main:app", host="0.0.0.0", port=SERVICE_PORT, log_config=None,  # 🔥 关键：禁止 uvicorn 覆盖 logging
		access_log=True,  # 可选：确保 access log 打开
	)
	server = uvicorn.Server(config)
	import asyncio
	
	asyncio.get_event_loop().run_until_complete(server.serve())
