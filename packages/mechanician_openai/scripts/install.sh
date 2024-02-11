#!/bin/bash

cd ../mechanician &&
./scripts/install.sh &&
cd ../mechanician_openai/src &&
pip install -e .
