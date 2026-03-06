# app/common/result.py
import time
from datetime import datetime
from typing import Generic, TypeVar, Optional, List, Dict

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class Result(GenericModel, Generic[T]):
	success: bool = True
	message: str = "操作成功！"
	code: int = 0
	result: Optional[T] = None
	timestamp: int = int(time.time() * 1000)
	
	@staticmethod
	def ok(data: Optional[T] = None,
		   msg: str = "操作成功！"):
		return Result(success=True,
					  message=msg,
					  code=200,
					  result=data,
					  timestamp=int(time.time() * 1000), 
		              )
	
	@staticmethod
	def error(msg: str,
			  code: int = 500,
			  data: Optional[T] = None):
		return Result(success=False,
					  message=msg,
					  code=code,
					  result=data,
					  timestamp=int(time.time() * 1000), )




