#!/bin/bash

cd svm_proprank
make

cd ../lib/pyrankagg
python setup.py install

cd ../../
pip install -r requirements.txt