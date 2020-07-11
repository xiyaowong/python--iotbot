from iotbot import Action, EventMsg


def receive_events(ctx: EventMsg):
    # 这样写是因为第一次整这个插件时事件上下文还是字典，
    # 这里我因为懒得改了，所以这样写
    # 用对象的字段会方便和简洁一点，自己修改吧
    ctx = ctx.message    #
    ######################
    action = Action(ctx['CurrentQQ'])
    data = ctx['CurrentPacket']['Data']

    # 欢迎新群员
    if data['EventName'] == "ON_EVENT_GROUP_JOIN":
        uid = data['EventData']['UserID']
        uname = data['EventData']['UserName']
        gid = data['EventMsg']['FromUin']
        action.send_group_text_msg(
            gid,
            '欢迎<%s>入群！[表情175]' % uname,
            uid
        )
        return

    # 群友退群
    if data['EventName'] == "ON_EVENT_GROUP_EXIT":
        uid = data['EventData']['UserID']
        gid = data['EventMsg']['FromUin']
        action.send_group_text_msg(
            gid,
            f'群友【{uid}】\n[表情107]离开了本群！\n[表情66]请珍惜在一起的每一分钟！'
        )
        return
