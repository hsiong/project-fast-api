import json
import logging
from types import SimpleNamespace


def dict_to_bean(obj): 
	"""
	将 dict/list 递归转换为支持 bean.a.b.c 的对象
	"""
	if isinstance(obj, dict): 
		return SimpleNamespace(**{k: dict_to_bean(v) for k, v in obj.items()})
	elif isinstance(obj, list): 
		return [dict_to_bean(i) for i in obj]
	else: 
		return obj

def str_to_bean(text: str):
	return dict_to_bean(json.loads(text))

def clean_to_bean(text: str):
	# STEP 1: 清理 ``` 包裹
	t = text.strip()
	if t.startswith("```"):
		lines = t.splitlines()
		if lines[-1].strip().startswith("```"):
			t = "\n".join(lines[1:-1]).strip()
	
	# STEP 2: 尝试解析 JSON
	try:
		data = str_to_bean(t)
	except Exception as e:
		logging.error(f"LLM JSON 解析失败: {e}")
		data = None
	
	return data

def clean_to_str(text: str):
	# STEP 1: 清理 ``` 包裹
	t = text.strip()
	if t.startswith("```"):
		lines = t.splitlines()
		if lines[-1].strip().startswith("```"):
			t = "\n".join(lines[1:-1]).strip()
	
	return t

def clean_to_dict(text: str):
	# STEP 2: 尝试解析 JSON
	try:
		return clean_to_dict_raise(text)
	except Exception as e:
		logging.error(f"LLM JSON 解析失败: {e}")
		data = {}
	
	return data


def clean_to_dict_raise(text: str):
	# STEP 1: 清理 ``` 包裹
	t = text.strip()
	if t.startswith("```"):
		lines = t.splitlines()
		if lines[-1].strip().startswith("```"):
			t = "\n".join(lines[1:-1]).strip()
	data = json.loads(t)
	if not isinstance(data, dict):
		raise Exception("not dict")
	
	return data