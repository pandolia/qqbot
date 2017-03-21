sudo pip install virtualenv

mkdir ~/Py3Venv
cd ~/Py3Venv
virtualenv --python=python3 --no-site-packages qqbot-venv

cd qqbot-venv/bin/
source activate

pip install requests==2.7.0
pip install certifi==2015.4.28
pip install flask==0.12

pip install qqbot

# 重新打开终端后，在使用 qqbot 和 qq 命令之前，需要运行：
# source ~/Py3Venv/qqbot-venv/bin/activate
