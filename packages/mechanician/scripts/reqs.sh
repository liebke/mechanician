#!/bin/bash

cd ./src &&
python3 setup.py sdist
pip freeze > ../requirements.txt
