# -*- coding: utf-8 -*-

from setuptools import setup

version = '1.9.7'

setup(
    name = 'qqbot',
    version = version,
    packages = ['qqbot'],
    entry_points = {
        'console_scripts': [
            'qqbot = qqbot:main',
        ]
    },
    install_requires = ['requests', 'certifi', 'flask'],
    description = "QQBot: A conversation robot base on Tencent's SmartQQ",
    author = 'pandolia',
    author_email = 'pandolia@yeah.net',
    url = 'https://github.com/pandolia/qqbot/',
    download_url = 'https://github.com/pandolia/qqbot/archive/%s.tar.gz' % \
                    version,
    keywords = ['QQBot', 'conversation robot', 'tencent', 'qq',
                'web', 'network', 'python', 'http'],
    classifiers = [],
)
