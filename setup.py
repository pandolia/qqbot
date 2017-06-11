# -*- coding: utf-8 -*-

from setuptools import setup

version = 'v2.3.1'

setup(
    name = 'qqbot',
    version = version,
    packages = ['qqbot', 'qqbot.qcontactdb', 'qqbot.plugins'],
    entry_points = {
        'console_scripts': [
            'qqbot = qqbot:RunBot',
            'qq = qqbot:QTerm'
        ]
    },
    install_requires = ['requests', 'certifi', 'apscheduler'],
    description = "QQBot: A conversation robot base on Tencent's SmartQQ",
    author = 'pandolia' ,
    author_email = 'pandolia@yeah.net',
    url = 'https://github.com/pandolia/qqbot/',
    download_url = 'https://github.com/pandolia/qqbot/archive/%s.tar.gz' % version,
    keywords = ['QQBot', 'conversation robot', 'tencent', 'qq',
                'web', 'network', 'python', 'http'],
    classifiers = [],
)
