#!/bin/bash
set -e

cd tests
if test -d model_document; then
	rm -rf model_document
fi
if test -d model_file; then
	rm -rf model_file
fi
oarepo-compile-model ./model_document.yaml --output-directory ./model_document
oarepo-compile-model ./model_file.yaml --output-directory ./model_file

cd model_document
pip install -e .
cd ..
cd model_file
pip install -e .
cd ..
cd ..

pip install py
pytest
