import time
from queue import deque

import requests
from iotbot import IOTBOT, Action, GroupMsg

bot_qq = 11111111
bot = IOTBOT(
    bot_qq,
    use_plugins=True
)
action = Action(bot)

master = 111111111  # 主人qq

# 用于自动回复功能
big_mouth_len = 3  # 连续多少条相同信息时+1
big_mouth_deque = deque(maxlen=big_mouth_len)
for i in range(big_mouth_len):
    big_mouth_deque.append(i)  # 初始化


@bot.on_group_msg
def on_group_msg(ctx: GroupMsg):
    # 不处理自身消息
    if ctx.FromUserId == ctx.CurrentQQ:
        return
    content = ctx.Content  # type: str

    # 刷新插件
    if ctx.FromUserId == master and content == '刷新插件':
        time.sleep(2)
        if bot.refresh_plugins():
            action.send_group_text_msg(ctx.FromGroupId, '好了')
        else:
            action.send_group_text_msg(ctx.FromGroupId, '失败了')
        time.sleep(2)
        return

    # 自动回复 +1
    # TODO: 要修改群号
    if ctx.FromGroupId == 111111111111:  # 这里只处理一个群聊
        if ctx.MsgType == 'TextMsg' and len(content) < 20:  # 只复读文本消息和不超长度
            big_mouth_deque.append(content)
            if len(set(big_mouth_deque)) == 1:
                action.send_group_text_msg(ctx.FromGroupId, content=content)
                for i in range(big_mouth_len):
                    big_mouth_deque.append(i)

    # 召唤群友(回执消息)
    if ctx.FromUserId == master and content == '召唤群友':
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
