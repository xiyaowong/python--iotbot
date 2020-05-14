import time

from iotbot import IOTBOT, Action, FriendMsg, GroupMsg

bot_qq = 11
bot = IOTBOT(bot_qq)
action = Action(bot_qq)
# action = Action()
# action.bind_bot(bot)


@bot.on_group_msg
def on_group_msg(ctx: GroupMsg):
    print(ctx.message)
    if ctx.Content == '.test':
        print('CurrentQQ: ', ctx.get('CurrentQQ'))
        print('CurrentPacket: ', ctx.get('CurrentPacket'))
        print('GroupName: ', ctx.FromGroupName)
        print(ctx.MsgType)
        print('发送图片：', action.send_group_pic_msg(ctx.FromGroupId, 'https://t.cn/A6Am7xYO'))
        print('发送闪照：', action.send_group_pic_msg(ctx.FromGroupId, 'https://t.cn/A6Am7xYO', flashPic=True))
        for i in range(1, 3):
            time.sleep(0.5)
            print(action.send_group_pic_msg(ctx.FromGroupId, picUrl='https://t.cn/A6Am7xYO', content=str(i)))
        print(action.send_group_text_msg(ctx.FromGroupId, content='\nOK', atUser=ctx.FromUserId))


@bot.on_friend_msg
def on_friend_msg(ctx: FriendMsg):
    print(ctx.message)
    if ctx.Content == '.test':
        print(ctx.Content)
        print(ctx.FromUin)
        print('OK')
        print('发送闪照：', action.send_friend_pic_msg(ctx.FromUin, 'https://t.cn/A6Am7xYO', flashPic=True))
        action.send_friend_text_msg(ctx.FromUin, '成功')
        action.send_friend_pic_msg(
            ctx.FromUin, picUrl='https://t.cn/A6Am7xYO')


@bot.on_event
def on_event(message: dict):
    # 事件暂时未处理，需要手动操作
    print(message)


if __name__ == "__main__":
    bot.run()
