import requests

from iotbot import IOTBOT
from iotbot import Action
from iotbot import GroupMsg

bot_qq = 123
bot = IOTBOT(bot_qq, use_plugins=True, plugin_dir='plugins')
action = Action(bot)


# 群消息中间件使用示例
def group_ctx_middleware(ctx):
    ctx.master = 333  # 主人qq


bot.register_group_context_middleware(group_ctx_middleware)
####################


@bot.on_group_msg
def on_group_msg(ctx: GroupMsg):
    # 不处理自身消息
    if ctx.FromUserId == ctx.CurrentQQ:
        return
    content = ctx.Content

    # ==========插件管理==========
    if ctx.FromUserId == ctx.master:  # 因为中间件添加了，所以可以直接访问
        if content == '刷新所有插件':
            bot.refresh_plugins()
            return
        elif content == '加载新插件':
            bot.load_plugins()
            return
        elif content.startswith('刷新插件'):  # 重载指定插件
            plugin_name = content[4:]
            bot.reload_plugin(plugin_name)
            return
        elif content == 'py插件':
            action.send_group_text_msg(
                ctx.FromGroupId,
                '\n'.join(bot.plugins)
            )
            return
    # ===========================

    # 召唤群友(回执消息)
    if ctx.FromUserId == ctx.master and content == '召唤群友':
        card = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID="107" templateID="1" action="viewReceiptMessage" brief="[回执消息]" m_resid="1tko/MQMaPR0jedOx6T8tbleZtAZudGqTFakakLqukDzuTjrZS1/1V1QEUnZ8/2Y" m_fileName="6828184148041033822" sourceMsgId="0" url="" flag="3" adverSign="0" multiMsgFlag="0"><item layout="29" advertiser_id="0" aid="0"><type>1</type></item><source name="" icon="" action="" appid="-1" /></msg>"""
        action.send_group_xml_msg(ctx.FromGroupId, content=card)
        return

    # nmsl
    if content == 'nmsl':
        action.send_group_text_msg(
            ctx.FromGroupId,
            requests.get('https://nmsl.shadiao.app/api.php?level=min&lang=zh_cn').text
        )
        return

    # 舔我
    if content == '舔我':
        action.send_group_text_msg(
            ctx.FromGroupId,
            '\n' + requests.get('https://chp.shadiao.app/api.php').text,
            ctx.FromUserId
        )
        return


if __name__ == "__main__":
    bot.run()
