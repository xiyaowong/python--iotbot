from typing import Any, Callable

from .model import EventMsg, FriendMsg, GroupMsg

GroupMsgReceiver = Callable[[GroupMsg], Any]
FriendMsgReceiver = Callable[[FriendMsg], Any]
EventMsgReceiver = Callable[[EventMsg], Any]
