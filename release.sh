#!/bin/bash

rm -rf build/ dist/ *.egg-info;  # clean
python setup.py sdist bdist_wheel;  # source dist + binary wheel
twine upload dist/*;  # upload
