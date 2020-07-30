import json

from .exceptions import InvalidConfigError


class _config:
    def __init__(self, c: dict) -> None:
        # 与iotbot 对应的配置
        self.host: str = c.get('host')

        port: str = c.get('port')
        if port is not None and port.isdigit():
            self.port = int(port)
        else:
            self.port = None

        # webhook 相关配置
        self.webhook: bool = c.get('webhook') or False
        self.webhook_post_url: str = c.get('webhook_post_url')

        webhook_timeout: str = c.get('webhook_timeout')
        if webhook_timeout is not None and webhook_timeout.isdigit():
            self.webhook_timeout = int(webhook_timeout)
        else:
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
