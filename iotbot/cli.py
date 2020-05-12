import argparse
import os


def cli():
    parser = argparse.ArgumentParser(description='iotbot模板生成')
    parser.add_argument('-n', default='bot', type=str, help='生成的文件名')
    parser.add_argument('-q', default=12345678, type=int, help='机器人QQ号')

    args = parser.parse_args()
    fileName = args.n
    q = args.q

    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.py')

    c = input(f'将创建{fileName}.py文件, 机器人QQ为：{q}。是否确定？ y/N: ')
    if c.lower() == 'y':
        with open(template_path, 'r') as f:
            temp = f.read()

        temp = temp.replace('bot_qq = 11', f'bot_qq = {q}')

        with open(f'{fileName}.py', 'w') as f:
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
