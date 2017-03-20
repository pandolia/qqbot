

#### 1.采用 virtualenv 将本项目安装至独立的运行环境

本项目依赖于 reqests 、flask 和 certifi 库，用 pip 安装本项目时会自动安装以上三个库以及它们所依赖的库。一般来说安装本项目不会与系统其他项目冲突，因此可直接安装至系统的全局 site-packages 目录。

在某些系统中可能会出现 https 请求错误，这时需要安装 certifi 库的指定版本（2015.4.28 版），可能会将系统中已有的 certifi 库升级或降级，可能会使系统中的其他项目无法使用，这时可以使用 virtualenv 将本项目安装至独立的运行环境中。

virtualenv 基本原理和使用可参考 [廖雪峰的教程](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432712108300322c61f256c74803b43bfd65c6f8d0d0000) 。

以下脚本将在 ~/PyVenv/qqbot-venv 目录下创建一个独立的运行环境，并将 qqbot 及其依赖的库安装至 ~/PyVenv/qqbot-env/lib/site-packages 目录下。系统中的原有的库不会被改动，其他项目不受影响。

    sudo pip install virtualenv

    mkdir ~/PyVenv
    cd ~/PyVenv
    virtualenv --no-site-packages qqbot-venv

    source ~/PyVenv/qqbot-env/bin/activate

    pip install requests==2.7.0
    pip install certifi==2015.4.28
    pip install flask==0.12
    pip install qqbot

注意：使用本方式安装本项目后，每次使用 qqbot 和 qq 命令之前，需要先运行下面这条命令激活 qqbot-venv 下的运行环境：

    source ~/PyVenv/qqbot-env/bin/activate
