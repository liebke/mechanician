#!/bin/bash

cd ../mechanician &&
./install.sh &&
cd ../mechanician_openai/src &&
pip install -e .
