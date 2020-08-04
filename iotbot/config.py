import json

from .exceptions import InvalidConfigError


class _config:
    def __init__(self, c: dict) -> None:
        # 与iotbot 对应的配置, 不存在只能为None
        self.host = str(c.get('host'))
        try:
            self.port = int(c.get('port'))
        except ValueError:
            self.port = None

        # webhook 相关配置
        self.webhook = bool(c.get('webhook'))
        self.webhook_post_url = str(c.get('webhook_post_url'))

        try:
            self.webhook_timeout = int(c.get('webhook_timeout'))
        except ValueError:
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
