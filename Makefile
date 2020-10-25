.PHONY: test clean install run push

test: 
	pytest

clean: clean-build clean-pyc clean-test 

clean-build: 
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: 
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: 
	rm -fr .pytest_cache

install: clean 
	python setup.py install

run:
	python app/main.py

push:
	git add .
	git commit -m "$m"
	git push origin master
