from iotbot.sugar import Text
from iotbot.decorators import equal_content

# 下面三个函数名不能改，否则不会调用
# 但是都是可选项，建议把不需要用到的函数删除，节约资源


@equal_content('middleware')
def receive_group_msg(ctx):
    print('------------------')
    print(dir(ctx))
    if hasattr(ctx, 'master'):
        print(ctx.master)
        print(type(ctx))
        Text(ctx.master)
