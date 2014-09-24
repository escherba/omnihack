.PHONY: clean virtualenv upgrade test package dev dist

PYENV = . env/bin/activate;
PYTHON = $(PYENV) python
PYTHON_TIMED = $(PYENV) time python

package: env
	$(PYTHON) setup.py bdist_egg
	$(PYTHON) setup.py sdist

test: dev
	$(PYENV) nosetests $(NOSEARGS)
	$(PYENV) py.test README.rst

dev: dev_requirements.txt env
	$(PYENV) pip install -e . -r $<

dist:
	$(PYTHON) setup.py sdist

clean:
	$(PYTHON) setup.py clean
	rm -rf dist build
	find . -type f -name "*.pyc" -exec rm {} \;

nuke: clean
	rm -rf *.egg *.egg-info env bin cover coverage.xml nosetests.xml

env virtualenv: env/bin/activate
env/bin/activate: requirements.txt setup.py
	test -f $@ || virtualenv --no-site-packages env
	$(PYENV) pip install -e . -r $<
	touch $@
