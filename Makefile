.PHONY: clean
clean:
	find . -name "logs.txt" -delete

format:
	yapf -i --recursive .
