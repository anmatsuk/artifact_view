* Run the tests: (need Python3 version, because Python2 doesn't work correctly with SIGINT interruption in thread)

```
pip install virtualenv
virtualenv --python=python3 venv3
source venv3/bin/activate
pip install -r requirements.txt
py.test -vv
```
