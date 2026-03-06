import logging
import os
from logging.handlers import TimedRotatingFileHandler

from config.settings import LOG_PATH, LOG_NAME


def setup_logging() -> None:
	log_dir = os.path.expanduser(LOG_PATH)
	os.makedirs(log_dir, exist_ok=True)
	
	# 🔥 使用 root logger（关键）
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)
	
	# 防止重复添加 handler
	if logger.handlers:
		return
	
	formatter = logging.Formatter(
		"%(asctime)s - %(levelname)s - %(name)s - %(message)s"
	)
	
	# 📁 每天一个日志文件 - 当天写入 LOG_NAME.log ； 历史写入 LOG_NAME-YYYY-MM-DD.log
	file_handler = TimedRotatingFileHandler(
		filename=os.path.join(log_dir, f"{LOG_NAME}.log"),
		when="midnight",
		interval=1,
		backupCount=14,
		encoding="utf-8"
	)
	file_handler.suffix = "%Y-%m-%d"
	file_handler.setFormatter(formatter)
	
	# 🖥 控制台输出（可选，建议保留）
	console_handler = logging.StreamHandler()
	console_handler.setFormatter(formatter)
	
	logger.addHandler(file_handler)
	logger.addHandler(console_handler)
