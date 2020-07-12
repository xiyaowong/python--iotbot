from iotbot import IOTBOT
from iotbot import Action
from iotbot import EventMsg
from iotbot import FriendMsg
from iotbot import GroupMsg

bot_qq = 11
bot = IOTBOT(bot_qq, use_plugins=False)
action = Action(bot)


@bot.on_group_msg
def on_group_msg(ctx: GroupMsg):
    print(ctx.message)
    if ctx.Content == '刷新插件':
        bot.refresh_plugins()
    if ctx.Content == '.test':
        action.send_group_pic_msg(ctx.FromGroupId, 'https://t.cn/A6Am7xYO')


@bot.on_friend_msg
def on_friend_msg(ctx: FriendMsg):
    print(ctx.message)
    if ctx.Content == '.test':
        action.send_friend_pic_msg(ctx.FromUin, picUrl='https://t.cn/A6Am7xYO')


@bot.on_event
def on_event(ctx: EventMsg):
    print(ctx.message)
    print(ctx.EventName)


def test_group(ctx: GroupMsg):
    print('In test_group', ctx.FromNickName)


bot.add_group_msg_receiver(test_group)

if __name__ == "__main__":
    print(bot.receivers)
    bot.run()
