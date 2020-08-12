import re
from typing import List

from .exceptions import InvalidConfigError

try:
    import ujson as json
except Exception:
    import json


def _check_schema(url: str) -> str:
    if not re.findall(r'(http://|https://)', url):
        return "http://" + url
    return url


class _config:
    def __init__(self, c: dict) -> None:
        # 与iotbot 对应的配置, 不存在只能为None
        host = c.get('host')
        if host:
            self.host = _check_schema(str(host))
        else:
            self.host = None

        try:
            self.port = int(c.get('port'))
        except Exception:
            self.port = None

        self.group_blacklist: List[int] = c.get('group_blacklist')  # 群黑名单
        self.friend_blacklist: List[int] = c.get('friend_blacklist')  # 好友黑名单

        # webhook 相关配置
        self.webhook = bool(c.get('webhook'))
        webhook_post_url = c.get('webhook_post_url')
        if webhook_post_url:
            self.webhook_post_url = _check_schema(str(webhook_post_url))
        else:
            self.webhook_post_url = None

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
