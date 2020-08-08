from typing import Any
from typing import Callable

from .model import EventMsg
from .model import FriendMsg
from .model import GroupMsg

GroupMsgReceiver = Callable[[GroupMsg], Any]
FriendMsgReceiver = Callable[[FriendMsg], Any]
EventMsgReceiver = Callable[[EventMsg], Any]
