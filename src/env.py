try:
    from config.secrets import env as env_secrets
except ImportError:
    env_secrets = {}
from default_config import env as env_default


def envget(option):
    if option is None or len(option) == 0:
        raise ValueError("empty or  null option string")
    array = option.split('.')
    tmp = env_secrets
    for x in array:
        if type(tmp) is not dict:
            break
        tmp = tmp.get(x)
    if tmp is not None:
        return tmp
    tmp = env_default
    for x in array:
        tmp = tmp.get(x)
        if tmp is None:
            raise ValueError("env variable not found: " + str(option))
    return tmp
