#!/bin/bash

cd ../mechanician &&
./scripts/install.sh &&
cd ../mechanician_ui &&
pip install -e .
