.PHONY: install run platforms history test clean
# Makefile biar perintah panjang jadi pendek. `make install`, `make test`, dst.

install:
	bash scripts/install.sh

platforms:
	python3 -m grabin --platforms

history:
	python3 -m grabin --history

test:
	python3 -m unittest discover -s tests -v

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -name "*.pyc" -delete
