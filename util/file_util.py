import base64
import textwrap
import requests


def read_file(file_path):
	"""
	读取文件
	:param file_path: 
	:return: 
	"""
	with open(file_path, 'r', encoding='utf-8') as f:
		content = f.read()
	
	return content


def url_to_base64(url):
	r = requests.get(url, timeout=30)
	r.raise_for_status()
	return base64.b64encode(r.content).decode()