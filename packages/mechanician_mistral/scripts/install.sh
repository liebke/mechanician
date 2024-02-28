#!/bin/bash

cd ../mechanician &&
./scripts/install.sh &&
cd ../mechanician_mistral &&
pip install -e .
