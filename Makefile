run:
	python run.py

test:
	python -m unittest discover -s tests

coverage:
	coverage run -m unittest discover -s tests
