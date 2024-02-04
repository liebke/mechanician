#!/bin/bash

cd ../mechanician_core &&
./install.sh &&
cd ../mechanician_openai/src &&
pip install -e .
