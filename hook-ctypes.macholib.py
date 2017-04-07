# -*- coding: utf-8 -*-
# 本文件是 pyinstaller 打包用的，打包命令：
# pyinstaller -F main.py --additional-hooks-dir=.
from PyInstaller.utils.hooks import copy_metadata
datas = copy_metadata('apscheduler')
