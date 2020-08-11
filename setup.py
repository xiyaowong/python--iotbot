import io

from setuptools import setup


def read_files(files):
    data = []
    for file in files:
        with io.open(file, encoding='utf-8') as f:
            data.append(f.read())
    return "\n".join(data)


long_description = read_files(['README.md', 'CHANGELOG.md'])

meta = {}

with io.open('./iotbot/version.py', encoding='utf-8') as f:
    exec(f.read(), meta)

setup(
    name="python-iotbot",
    description="IOTBOT SDK with python!",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=meta['__version__'],
    author="wongxy",
    author_email="xiyao.wong@foxmail.com",
    url="https://github.com/XiyaoWong/python-iotbot",
    license='MIT',
    keywords=['iotbot', 'iotbot sdk', 'iotqq'],
    packages=['iotbot'],
    install_requires=[
        'python-socketio >= 4.5.1', 'websocket-client >= 0.57.0',
        'requests >= 2.23.0', 'prettytable >= 0.7.2', 'loguru >= 0.5.1'
    ],
    entry_points='''
        [console_scripts]
        iotbot=iotbot.cli:cli
    ''',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6'
)
