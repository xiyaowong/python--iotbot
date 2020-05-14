# pylint: disable=too-many-instance-attributes
class GroupMsg:
    def __init__(self, message: dict):
        self.message = message
        self.CurrentQQ = message.get('CurrentQQ')

        # ========================================
        # 代码提示
        self.FromGroupId = 0
        self.FromGroupName = ''
        self.FromUserId = 0
        self.FromNickName = ''
        self.Content = ''
        self.MsgType = ''
        self.MsgTime = 0
        self.MsgSeq = 0
        self.MsgRandom = 0
        self.RedBaginfo = None
        # ========================================

        temp = message.get('CurrentPacket')
        data = temp.get('Data') if temp is not None else {}

        self.data = data

        self.__init(data)

    def __init(self, data):
        for attr in ['FromGroupId',
                     'FromGroupName',
                     'FromUserId',
                     'FromNickName',
                     'Content',
                     'MsgType',
                     'MsgTime',
                     'MsgSeq',
                     'MsgRandom',
                     'RedBaginfo']:
            setattr(self, attr, data.get(attr))

    def get(self, item):
        return self.message.get(item)

    def __getitem__(self, item):
        return self.message.get(item)

    def __dict__(self, item):
        return self.message.get(item)


class FriendMsg:
    def __init__(self, message: dict):
        self.message = message
        self.CurrentQQ = message.get('CurrentQQ')

        # ========================================
        # 代码提示
        self.FromUin = 0
        self.ToUin = 0
        self.MsgType = ''
        self.MsgSeq = 0
        self.Content = ''
        self.RedBaginfo = None
        # ========================================

        temp = message.get('CurrentPacket')
        data = temp.get('Data') if temp is not None else {}

        self.data = data

        self.__init(data)

    def __init(self, data):
        for attr in ['FromUin',
                     'ToUin',
                     'MsgType',
                     'MsgSeq',
                     'Content',
                     'RedBaginfo']:
            setattr(self, attr, data.get(attr))

    def get(self, item):
        return self.message.get(item)

    def __getitem__(self, item):
        return self.message.get(item)

    def __dict__(self, item):
        return self.message.get(item)


model_map = {
    'OnGroupMsgs': GroupMsg,
    'OnFriendMsgs': FriendMsg,
    # 'OnEvents':EventMsg

}
