#!/bin/bash
set -e
cd tests
for model in model_document model_document_no_expandable_fields model_document_picture model_file model_picture
do
    if test -d $model; then
	    rm -rf $model
    fi
    oarepo-compile-model "./$model.yaml" --output-directory "./$model" -vvv
    cd $model
    pip install -e .
    cd ..
done
cd ..
#export OPENSEARCH_PORT=9400
pytest
