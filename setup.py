# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name = 'qqbot',
    version = '1.13',
    packages = ['qqbot'],
    scripts = ['qqbot/qqbot', 'qqbot/qqbot.py'],
    description = "QQBot: A conversation robot base on Tencent's SmartQQ",
    author = 'pandolia',
    author_email = 'pandolia@yeah.net',
    url = 'https://github.com/pandolia/qqbot/',
    download_url = 'https://github.com/pandolia/qqbot/archive/v1.13.tar.gz',
    keywords = ['QQBot', 'conversation robot', 'tencent', 'qq', 'web', 'network', 'python', 'http'],
    classifiers = [],
)
