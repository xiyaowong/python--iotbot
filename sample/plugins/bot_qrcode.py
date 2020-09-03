'''
生成二维码+{数据(文字)}
'''
import base64
import io

from iotbot import FriendMsg, GroupMsg
from iotbot.decorators import in_content, not_botself
from iotbot.sugar import Picture

try:
    import qrcode
except ImportError:
    raise ImportError('请先安装依赖库: pip install qrcode, pillow')


def gen_qrcode(text: str) -> str:
    img = qrcode.make(text)
    img_buffer = io.BytesIO()
    img.save(img_buffer)
    return base64.b64encode(img_buffer.getvalue()).decode()


@not_botself
@in_content('生成二维码')
def receive_group_msg(ctx: GroupMsg):
    Picture(pic_base64=gen_qrcode(ctx.Content.replace('生成二维码', '')))


@not_botself
@in_content('生成二维码')
def receive_friend_msg(ctx: FriendMsg):
    Picture(pic_base64=gen_qrcode(ctx.Content.replace('生成二维码', '')))
