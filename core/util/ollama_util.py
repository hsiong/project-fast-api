import base64

import requests

from core.config.settings import OLLAMA_CHAT_URL, OLLAMA_GENERATE_URL
from core.util.bean_util import dict_to_bean


def run_llm_messages(messages: list, model, thinking=False):
	payload = {
		"model": model, "messages": messages, "stream": False, "think": thinking, "options": {
			"num_ctx": 20960,  # 用满模型支持的 40K 窗口
			"num_predict": 8000,  # 允许最多生成 8000 tokens（你可以按需调大/调小）
			"verbose": True,  # 输出详细信息
		}
	}
	resp = requests.post(OLLAMA_CHAT_URL, json=payload)
	data = resp.json()
	print(f'prompt_eval_count tokens: {data.get("prompt_eval_count")}')
	print(f'eval_count tokens: {data.get("eval_count")}')  # 模型为生成输出时所计算的 token 数量
	print(f'ret word count: {len(data.get("message"))}')
	return data.get('message').get('content')


def run_llm(prompt_competition, model, thinking=False):
	print(f'len prompt_competition: {len(prompt_competition)}')
	
	payload = {
		"model": model, "prompt": prompt_competition, "stream": False, "think": thinking, "options": {
			"num_ctx": 20960,  # 用满模型支持的 40K 窗口
			"num_predict": 10000,  # 允许最多生成 8000 tokens（你可以按需调大/调小）
			"verbose": True,  # 输出详细信息
		}
	}
	resp = requests.post(OLLAMA_GENERATE_URL, json=payload)
	data = resp.json()
	print(f'prompt_eval_count tokens: {data.get("prompt_eval_count")}')
	print(f'eval_count tokens: {data.get("eval_count")}')  # 模型为生成输出时所计算的 token 数量
	print(f'ret word count: {len(data.get("response"))}')
	return data.get("response")


def url_to_base64(url):
	r = requests.get(url, timeout=30)
	r.raise_for_status()
	return base64.b64encode(r.content).decode()


def file_to_base64(img_path):
	"""
	Encode a local image file path to base64 for Ollama vision requests.
	:param img_path:
	:return:
	"""
	with open(img_path, "rb") as image_file:
		return base64.b64encode(image_file.read()).decode()


def run_llm_vl(prompt_competition, img_url, model="qwen3-vl:8b", timeout: int = 120) -> str:
	"""
	多模态图片识别
	:param prompt_competition: 
	:param img_url: 
	:param model: 
	:param timeout: 
	:return: 
	"""
	try:
		img_b64 = url_to_base64(img_url)
		resp = requests.post(OLLAMA_GENERATE_URL, json={
			"model": model, "prompt": prompt_competition, "images": [img_b64], "stream": False
		}, timeout=timeout)
		
		data = resp.json()
		print(f'prompt_eval_count tokens: {data.get("prompt_eval_count")}')
		print(f'eval_count tokens: {data.get("eval_count")}')  # 模型为生成输出时所计算的 token 数量
		print(f'ret word count: {len(data.get("response"))}\n')
		ret_str = dict_to_bean(data).response
		return ret_str.strip()
	except Exception as e:
		# 线上建议打日志,这里简单兜底
		raise e


def run_llm_vl_file(prompt_competition, img_path, model="qwen3-vl:8b", timeout: int = 120) -> str:
	"""
	多模态本地图片识别
	:param prompt_competition:
	:param img_path:
	:param model:
	:param timeout:
	:return:
	"""
	try:
		img_b64 = file_to_base64(img_path)
		resp = requests.post(OLLAMA_GENERATE_URL, json={
			"model": model, "prompt": prompt_competition, "images": [img_b64], "stream": False
		}, timeout=timeout)
		
		data = resp.json()
		print(f'prompt_eval_count tokens: {data.get("prompt_eval_count")}')
		print(f'eval_count tokens: {data.get("eval_count")}')  # 模型为生成输出时所计算的 token 数量
		print(f'ret word count: {len(data.get("response"))}\n')
		ret_str = dict_to_bean(data).response
		print(f'result: {ret_str}')
		return ret_str.strip()
	except Exception as e:
		# 线上建议打日志,这里简单兜底
		raise e
