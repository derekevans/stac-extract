
-include tasks/Makefile.*

install:
	python -m pip install -U wheel setuptools
	python -m pip install -e .
	python -m pip install --no-build-isolation --no-cache-dir --force-reinstall GDAL==3.11.0


