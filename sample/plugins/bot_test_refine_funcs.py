from iotbot import Action, EventMsg, FriendMsg, GroupMsg
from iotbot import refine_message as refine
from iotbot.decorators import not_botself
from iotbot.sugar import Picture, Text

# refine_?函数只是方便解析一些消息变化的部分
# 一般用在`事件`消息上，因为每个事件都有很多不同的数据
# 其他的用处主要在需要解析图片，语音之类的信息吧


@not_botself  # 忽略机器人自己的消息
def receive_group_msg(ctx: GroupMsg):
    # 群红包消息
    redbag_ctx = refine.refine_RedBag_group_msg(ctx)
    if redbag_ctx is not None:
        Text(redbag_ctx.RedBag_Authkey)  # 如果是红包，就在刚才的群内发送刚才红包的`AuthKey`字段
        del redbag_ctx
        return


@not_botself
def receive_friend_msg(ctx: FriendMsg):
    # 好友图片消息
    pic_ctx = refine.refine_pic_friend_msg(ctx)
    if pic_ctx is not None:
        print('----friend------------')
        Text(pic_ctx.GroupPic[0]['Url'])  # 给他发送刚才图片的链接
        del pic_ctx
        return
    # 好友语音消息
    voice_ctx = refine.refine_voice_friend_msg(ctx)  # 给他发送刚才语音的链接
    if voice_ctx is not None:
        Text(voice_ctx.VoiceUrl)
        del voice_ctx
        return


def receive_events(ctx: EventMsg):
    print(ctx.EventName)  # 打印事件名

    # 群消息撤回事件
    revoke_ctx = refine.refine_group_revoke_event_msg(ctx)
    if revoke_ctx is not None:
        print('------------------')
        print(revoke_ctx.AdminUserID)  # 谁撤回的
        print(revoke_ctx.UserID)  # 撤回谁的
        print('------------------')
        del revoke_ctx
        return

    # 群禁言事件
    shut_ctx = refine.refine_group_shut_event_msg(ctx)
    if shut_ctx is not None:
        if shut_ctx.UserID != 0:  # 没有特定的用, 为0说明是全体禁言
            if shut_ctx.ShutTime == 0:  # 为0是解除
                msg = '{}被解除禁言了'.format(shut_ctx.UserID)
            else:
                msg = '{}被禁言了{}分钟, 哈哈哈哈哈'.format(
                    shut_ctx.UserID, shut_ctx.ShutTime / 60
                )
            print(msg)
            if shut_ctx.UserID != shut_ctx.CurrentQQ:  # 如果不是自己被禁言，就发送给该群消息
                Action(shut_ctx.CurrentQQ).send_group_text_msg(shut_ctx.FromUin, msg)
        else:
            if shut_ctx.ShutTime == 0:
                print(f'{shut_ctx.FromUin}解除全体禁言')
            else:
                print(f'{shut_ctx.FromUin}全体禁言')
        del shut_ctx
        return

    # 某人加群事件
    join_ctx = refine.refine_group_join_event_msg(ctx)
    if join_ctx is not None:
        Action(join_ctx.CurrentQQ).send_group_text_msg(
            join_ctx.FromUin, '欢迎 <%s>' % join_ctx.UserName
        )
        del join_ctx
        return

    # 某人退群事件
    exit_ctx = refine.refine_group_exit_event_msg(ctx)
    if exit_ctx is not None:
        Action(exit_ctx.CurrentQQ).send_group_text_msg(
            exit_ctx.FromUin, f'群友<{exit_ctx.UserID}>离开了我们'
        )
        del exit_ctx
        return
