#!/bin/bash

cd ../mechanician &&
./scripts/install.sh &&
cd ../mechanician_arangodb/src &&
pip install -e .
pip install -e ".[dev]"
