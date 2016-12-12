python setup.py register -r pypitest
python setup.py sdist upload -r pypitest
python setup.py register -r pypi
python setup.py sdist upload -r pypi
rm -r dist
rm -r qqbot.egg-info