#### 1.采用 virtualenv 将本项目安装至独立的运行环境

本项目依赖于 reqests 、flask 、 certifi 和 apscheduler 库，用 pip 安装本项目时会自动安装以上四个库以及它们所依赖的库。一般来说安装本项目不会与系统其他项目冲突，因此可直接安装至系统的全局 site-packages 目录。

在某些系统中可能会出现 https 请求错误，这时需要安装 certifi 库的指定版本（2015.4.28 版），可能会将系统中已有的 certifi 库升级或降级并导致会使系统中的其他项目无法使用，这时可以使用 virtualenv 将本项目安装至独立的运行环境中。

另外，Windows 下的用户有时需要使用 pyinstaller 打包自己利用 qqbot 开发的程序，此时也建议使用 virtualenv 将 qqbot 以及 pyinstaller 安装至独立的运行环境中，然后利用此环境中的 pyinstaller 进行打包。

virtualenv 基本原理和使用可参考 [廖雪峰的教程](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432712108300322c61f256c74803b43bfd65c6f8d0d0000) 。

以下脚本（Linux下）将在 ~/PyVenv/qqbot-venv 目录下创建一个独立的运行环境，并将 qqbot 及其依赖的库安装至 ~/PyVenv/qqbot-env/lib/site-packages 目录下。系统中的原有的库不会被改动，其他项目不受影响。

    sudo pip install virtualenv

    mkdir ~/PyVenv
    cd ~/PyVenv
    virtualenv --no-site-packages qqbot-venv

    source ~/PyVenv/qqbot-env/bin/activate

    pip install requests==2.7.0
    pip install certifi==2015.4.28
    pip install flask==0.12
    pip install apscheduler==3.3.1
    pip install qqbot

注意：使用本方式安装本项目后，每次使用 qqbot 和 qq 命令之前，需要先运行下面这条命令激活 qqbot-venv 下的运行环境：

    source ~/PyVenv/qqbot-env/bin/activate

Windows 下， 上述脚本改为：

    pip install virtualenv
    
    c:
    mkdir %UserProfile%\PyVenv
    cd %UserProfile%\PyVenv
    virtualenv --no-site-packages qqbot-env

    %UserProfile%\PyVenv\qqbot-env\Scripts\activate

    pip install requests==2.7.0
    pip install certifi==2015.4.28
    pip install flask==0.12
    pip install apscheduler==3.3.1
    pip install qqbot

其中 %UserProfile% 是用户主目录，Win7中为 C:\Users\xxx 目录。

Windows 下如果需要使用 pyinstaller 打包，还需要安装 pyinstaller 和 pypiwin32 ：

    pip install pyinstaller==3.2.1
    pip install pypiwin32==219

然后在 %UserProfile%\PyVenv\qqbot-env 下新建一个目录 myapp ：
    
    cd %UserProfile%\PyVenv\qqbot-env
    mkdir myapp
    cd myapp

在该目录下新建一个 main.py ，内容为：

    from qqbot import Main; Main()

再新建一个 hook-ctypes.macholib.py ，内容为：

    from PyInstaller.utils.hooks import copy_metadata
    datas = copy_metadata('apscheduler')

最后，输入以下命令将 main.py 打包为 dist\main.exe

    ..\Scripts\pyinstaller -F main.py --additional-hooks-dir=.
