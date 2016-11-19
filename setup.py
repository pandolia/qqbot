# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name = 'qqbot',
    version = '1.8.7',
    py_modules = ['qqbot'],
    entry_points = {
        'console_scripts': [
            'qqbot = qqbot:main',
        ]
    },
    install_requires = ['requests==2.7.0', 'certifi==2015.4.28', 'flask==0.11.1'],
    description = "QQBot: A conversation robot base on Tencent's SmartQQ",
    author = 'pandolia',
    author_email = 'pandolia@yeah.net',
    url = 'https://github.com/pandolia/qqbot/',
    download_url = 'https://github.com/pandolia/qqbot/archive/v1.8.7.tar.gz',
    keywords = ['QQBot', 'conversation robot', 'tencent', 'qq', 'web', 'network', 'python', 'http'],
    classifiers = [],
)
