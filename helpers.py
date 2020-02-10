import string
import random


def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for _ in range(y))


def base_url_from_env(env: str):
    env = env.lower()
    if env in ['test', 'dev', 'demo']:
        base_url = f'https://dmx{env}.dm-matrix.com/'
    elif env == 'prod':
        base_url = 'https://matrixcloud.dm-matrix.com/'
    else:
        raise Exception('Введена некорректная среда')
    return base_url
