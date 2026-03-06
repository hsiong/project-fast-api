import os


def smart_cast(val: str):
    val = val.strip()
    val_l = val.lower()
    if val_l == "true":
        return True
    if val_l == "false":
        return False
    if val_l == "none":
        return None
    if val.isdigit():
        return int(val)
    try:
        return float(val)
    except ValueError:
        # 去掉包裹引号（防御）
        if (
                (val.startswith('"') and val.endswith('"')) or
                (val.startswith("'") and val.endswith("'"))
        ):
            val = val[1:-1]
        return val


def load_env(filepath=".env.dev"):
    '''
    加载环境变量
    '''
    filepath = f'config/{filepath}'
    os_env_dict = {}
    if not os.path.exists(filepath):
        return
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if " " in line:
                line, comment = line.split(" ", 1)
            if "#" in line:
                line, comment = line.split("#", 1)
            if '=' in line:
                key, value = line.split('=', 1)
                os_env_dict[key.strip()] = smart_cast(value)
    
    return os_env_dict
