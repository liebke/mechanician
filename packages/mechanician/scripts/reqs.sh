#!/bin/bash

python3 setup.py sdist
pip freeze > ../requirements.txt
