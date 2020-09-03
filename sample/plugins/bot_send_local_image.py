import base64
import os
import random

from iotbot import Action, GroupMsg

"""
随机发送本地图片，假设图片文件夹是同目录的images文件夹
"""
here = os.path.abspath(os.path.dirname(__file__))
image_dir = os.path.join(here, 'images')
file_list = os.listdir(image_dir)


def receive_group_msg(ctx: GroupMsg):
    if '图片' in ctx.Content:
        random.seed(os.urandom(100))
        choose_file = os.path.join(image_dir, random.choice(file_list))  # 随机取出一张，完整路径
        # 二进制转base64
        with open(choose_file, 'rb') as f:
            content = f.read()
        b64_str = base64.b64encode(content).decode()

        Action(ctx.CurrentQQ).send_group_pic_msg(ctx.FromGroupId, picBase64Buf=b64_str)
