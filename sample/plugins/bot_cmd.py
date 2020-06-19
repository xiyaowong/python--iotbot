import os

from iotbot import Action, GroupMsg

master = 1234567  # 只允许自己用


def receive_group_msg(ctx: GroupMsg):
    if ctx.FromUserId == master and ctx.Content.startswith('cmd'):
        try:
            msg = str(os.popen(ctx.Content
                               .replace('sudo', '')
                               .replace('rm', '')
                               .replace('cmd', '')
                               .strip()).read())
        except Exception:
            msg = 'error'
        finally:
            Action(ctx.CurrentQQ).send_group_text_msg(ctx.FromGroupId, content=msg)
