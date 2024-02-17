#!/bin/bash

cd ../mechanician &&
./scripts/install.sh &&
cd ../mechanician_openai &&
pip install -e .
