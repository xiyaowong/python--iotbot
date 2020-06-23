from iotbot import Action


def receive_events(ctx: dict):
    action = Action(ctx['CurrentQQ'])
    data = ctx['CurrentPacket']['Data']

    # 群管理系统消息 申请加群 邀请加群等通知
    if data['EventName'] == "ON_EVENT_GROUP_ADMINSYSNOTIFY":
        # Action -11 同意 14 忽略 21 拒绝
        data['EventData']['Action'] = 11
        action.get_group_answer_invite(data['EventData'])
        return

    # 欢迎新群员
    if data['EventName'] == "ON_EVENT_GROUP_JOIN":
        uid = data['EventData']['UserID']
        uname = data['EventData']['UserName']
        gid = data['EventMsg']['FromUin']
        action.send_group_pic_msg(
            gid,
            picUrl="http://q1.qlogo.cn/g?b=qq&nk=%d&s=640" % uid,
            content="[秀图%d]欢迎【%s】加入[表情175][PICFLAG]" % (40002, uname)
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

    # 处理好友申请
    if data['EventName'] == "ON_EVENT_FRIEND_ADD":
        # Action - 1 忽略 2 同意 3 拒绝
        data['EventData']['Action'] = 2
        print(data['EventData'])
        action.get_friend_deal(data['EventData'])
        return

