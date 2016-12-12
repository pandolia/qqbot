python setup.py sdist upload -r pypitest
python setup.py sdist upload -r pypi
rm -r dist
rm -r qqbot.egg-info