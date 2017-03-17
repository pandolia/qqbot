sudo pip install virtualenv

mkdir ~/Py3Venv
cd ~/Py3Venv
virtualenv --python=python3 --no-site-packages qqbot-venv

cd qqbot-venv/bin/
source activate

pip install -r requirements.txt

pip install qqbot
