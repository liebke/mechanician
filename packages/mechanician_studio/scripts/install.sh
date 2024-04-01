#!/bin/bash

cd ../mechanician &&
./scripts/install.sh &&
cd ../mechanician_studio &&
pip install -e .
