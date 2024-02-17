#!/bin/bash

cd ../mechanician &&
./scripts/install.sh &&
cd ../mechanician_arangodb &&
pip install -e .
pip install -e ".[dev]"
