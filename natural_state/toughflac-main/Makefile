format:
		make isort
		make black
		make docstring

isort:
		isort -rc toughflac

black:
		black -t py27 toughflac

docstring:
		docformatter -r -i --blank --wrap-summaries 88 --wrap-descriptions 88 --pre-summary-newline toughflac

clean:
		find . -name '__pycache__' -delete -print -o -name '*.pyc' -delete -print
		rm -rf *.egg-info/ build/ dist/