#!/bin/bash

cd ../mechanician &&
./install.sh &&
cd ../mechanician_arangodb/src &&
pip install -e .
pip install -e ".[dev]"
