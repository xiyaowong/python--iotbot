import io

from setuptools import setup

with open('./README.md', encoding='utf-8') as f:
    long_description = f.read()

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
    install_requires=['python-socketio >= 4.5.1', 'websocket-client >= 0.57.0', 'requests >= 2.23.0'],
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
