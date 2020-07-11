"""Author: wongxy github.com/xiyaowong

from iotbot import IOTBOT, GroupMsg, FriendMsg, EventMsg

bot = IOTBOT(your_bot_qq)

@bot.on_group_msg
def group(ctx: GroupMsg):
    pass

@bot.on_friend_msg
def friend(ctx: FriendMsg):
    pass

@bot.on_event
def event(message: EventMsg):
    pass
"""

from .action import Action
from .client import IOTBOT
from .model import EventMsg, FriendMsg, GroupMsg, model_map
