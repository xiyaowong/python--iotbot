from typing import List

from .exceptions import InvalidConfigError
from .utils import check_schema

try:
    import ujson as json
except Exception:
    import json


class _config:
    def __init__(self, c: dict) -> None:
        # 与iotbot 对应的配置, 不存在只能为None
        # ip
        host = c.get('host')
        if host:
            self.host = check_schema(str(host))
        else:
            self.host = None
        # port
        try:
            self.port = int(c.get('port'))
        except Exception:
            self.port = None
        # 群黑名单
        self.group_blacklist: List[int] = c.get('group_blacklist')
        # 好友黑名单
        self.friend_blacklist: List[int] = c.get('friend_blacklist')

        # webhook 相关配置
        # 开关
        self.webhook = bool(c.get('webhook'))
        # 推送地址
        webhook_post_url = c.get('webhook_post_url')
        if webhook_post_url:
            self.webhook_post_url = check_schema(str(webhook_post_url))
        else:
            self.webhook_post_url = None
        # 推送等待延时
        try:
            self.webhook_timeout = int(c.get('webhook_timeout'))
        except Exception:
            self.webhook_timeout = 10


_config_dict = {}
try:
    with open('./.iotbot.json', encoding='utf-8') as f:
        _config_dict = json.load(f)
except FileNotFoundError:
    pass
except json.JSONDecodeError as e:
    raise InvalidConfigError('配置文件不规范') from e

config = _config(_config_dict)

# print('=====config=====')
# print('port: ', config.port)
# print('host: ', config.host)
# print('webhook: ', config.webhook)
# print('webhook_post_url: ', config.webhook_post_url)
# print('webhook_timeout: ', config.webhook_timeout)
# print('================')
