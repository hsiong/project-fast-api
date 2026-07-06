import inspect
import logging
import os
import time
from datetime import datetime
from functools import wraps

from core.model.result_bean import Result


def spel_resolve(expr: str, fn_args: dict):
    """
    解析 SPEL 风格的表达式，例如： "user.profile.id"
    从函数参数中层层取值
    """
    parts = expr.split(".")
    root = parts[0]

    if root not in fn_args:
        raise ValueError(f"SPEL 根变量 `{root}` 不存在于函数参数中")

    value = fn_args[root]

    # 层层解析 user.profile.id
    for attr in parts[1:]:
        if isinstance(value, dict):
            value = value.get(attr)
        else:
            value = getattr(value, attr, None)

        if value is None:
            raise ValueError(f"SPEL 表达式 `{expr}` 无法解析，字段 `{attr}` 不存在")

    return value


def log_run_to_file_async(file_path: str, log_key: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):  # ⭐ async
            signature = inspect.signature(func)
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            fn_args = bound.arguments

            l_key = "UNKNOWN"
            error_msg = ""
            status = "SUCCESS"
            func_name = func.__name__

            try:
                l_key = spel_resolve(log_key, fn_args)
            except Exception as e:
                error_msg = f"SPEL_PARSE_ERROR: {e}"
                logging.exception(error_msg)

            start_time = time.time()
            try:
                return await func(*args, **kwargs)  # ⭐ await
            except Exception as e:
                status = "ERROR"
                error_msg = f"{type(e).__name__}: {e}"
                logging.exception(error_msg)
                raise
            finally:
                elapsed = time.time() - start_time
                log_line = (
                    f"status={status}, "
                    f"l_key={l_key}, "
                    f"elapsed={elapsed:.4f}, "
                    f'info="{error_msg}"\n'
                )
                try:
                    file_dir = f"{file_path}/log_wrapper"
                    os.makedirs(file_dir, exist_ok=True)
                    file_name = f"{file_dir}/{func_name}_{datetime.now().strftime('%Y%m%d')}.csv"
                    with open(file_name, "a", encoding="utf-8") as f:
                        f.write(log_line)
                except IOError:
                    logging.exception("写日志失败")

        return wrapper

    return decorator


def log_run_to_file(file_path: str, log_key: str):
    """
    支持 SPEL 风格 profile_id 表达式：
    @log_run_to_file("/tmp/logs", profile_id="user.profile.id")
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # --- 将 args + kwargs 统一成一个参数名->值的 dict ---
            signature = inspect.signature(func)
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            fn_args = bound.arguments  # ⇒ OrderedDict

            # --- 解析 SPEL 表达式 ---
            try:
                l_key = spel_resolve(log_key, fn_args)
            except Exception as e:
                raise ValueError(f"无法从 SPEL `{log_key}` 解析 log_name: {e}")

            # --------------------------------------------------

            start_time = time.time()
            status = "SUCCESS"
            error_msg = ""
            func_name = func.__name__

            try:
                return func(*args, **kwargs)
            except Exception as e:
                status = "ERROR"
                error_msg = f"{type(e).__name__}: {str(e)}"
                logging.error(error_msg, e)
                return Result.error(error_msg)
            finally:
                elapsed = time.time() - start_time
                log_line = (
                    f"status={status}, "
                    f"l_key={l_key}, "
                    f"elapsed={elapsed:.4f}, "
                    f'info="{error_msg}"\n'
                )

                try:
                    file_dir = f"{file_path}/log_wrapper"
                    if not os.path.exists(file_dir):
                        os.makedirs(file_dir)
                    file_name = f"{file_dir}/{func_name}_{datetime.now().strftime('%Y%m%d')}.csv"
                    with open(file_name, "a", encoding="utf-8") as f:
                        f.write(log_line)
                except IOError as io_err:
                    print("写文件错误:", io_err)

        return wrapper

    return decorator
