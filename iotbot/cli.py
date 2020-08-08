import argparse
import os


def cli():
    parser = argparse.ArgumentParser(description='iotbot模板生成')
    parser.add_argument('-n', default='bot', type=str, help='生成的文件名')
    parser.add_argument('-q', default=12345678, type=int, help='机器人QQ号')
    parser.add_argument('-p', default=None, type=str, help='插件名')

    args = parser.parse_args()
    fileName = args.n
    qq = args.q
    plug_name = args.p

    if plug_name is not None:
        file = f'bot_{plug_name}.py'
        if input(f'将生成{file}，这是覆盖写操作，确定？ y/N ').lower() == 'y':
            with open(file, 'w', encoding='utf-8') as f:
                f.write("""from iotbot import Action, FriendMsg, GroupMsg, EventMsg


# 下面三个函数名不能改，否则不会调用
# 但是都是可选项，建议把不需要用到的函数删除，节约资源

def receive_group_msg(ctx: GroupMsg):
    Action(ctx.CurrentQQ)

def receive_friend_msg(ctx: FriendMsg):
    Action(ctx.CurrentQQ)

def receive_events(ctx: EventMsg):
    Action(ctx.CurrentQQ)
    """)
            print('OK!')
            return
        else:
            print('bye~')
            return

    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.py')

    c = input(f'将创建{fileName}.py文件, 机器人QQ为：{qq}。是否确定？ y/N: ')
    if c.lower() == 'y':
        with open(template_path, 'r', encoding='utf-8') as f:
            temp = f.read()

        temp = temp.replace('bot_qq = 11', f'bot_qq = {qq}')

        with open(f'{fileName}.py', 'w', encoding='utf-8') as f:
            f.write(temp)

        print()
        print('创建成功~')
        print(f"""
执行如下命令：python {fileName}.py

在机器人所在的群或私聊机器人发送：.test
""")
    else:
        print('已取消操作')


if __name__ == "__main__":
    cli()
