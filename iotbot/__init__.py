"""Author: wongxy github.com/xiyaowong

from iotbot import IOTBOT, GroupMsg, FriendMsg

bot = IOTBOT(your_bot_qq)

@bot.on_group_msg
def group(ctx: GroupMsg):
    pass

@bot.on_friend_msg
def friend(ctx: FriendMsg):
    pass

@bot.on_event
def event(message: dict):
    pass
"""

from .client import IOTBOT
from .model import FriendMsg, GroupMsg, model_map
from .action import Action
