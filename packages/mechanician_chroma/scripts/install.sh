#!/bin/bash

cd ../mechanician &&
./scripts/install.sh &&
cd ../mechanician_chroma &&
pip install -e .
