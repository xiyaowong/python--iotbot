import json
import re

from .exceptions import InvalidConfigError


def _check_schema(url: str) -> str:
    if not re.findall(r'(http://|https://)', url):
        return "http://" + url
    return url


class _config:
    def __init__(self, c: dict) -> None:
        # 与iotbot 对应的配置, 不存在只能为None
        self.host = _check_schema(c.get('host'))
        try:
            self.port = int(c.get('port'))
        except Exception:
            self.port = None

        # webhook 相关配置
        self.webhook = bool(c.get('webhook'))
        self.webhook_post_url = _check_schema(c.get('webhook_post_url'))

        try:
            self.webhook_timeout = int(c.get('webhook_timeout'))
        except Exception:
            self.webhook_timeout = 10


config_dict = {}
try:
    with open('./.iotbot.json', encoding='utf-8') as f:
        config_dict = json.load(f)
except FileNotFoundError:
    pass
except json.JSONDecodeError as e:
    raise InvalidConfigError('配置文件不规范') from e

config = _config(config_dict)

# print('=====config=====')
# print('port: ', config.port)
# print('host: ', config.host)
# print('webhook: ', config.webhook)
# print('webhook_post_url: ', config.webhook_post_url)
# print('webhook_timeout: ', config.webhook_timeout)
# print('================')
