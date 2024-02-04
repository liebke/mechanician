#!/bin/bash

cd ../mechanician_core &&
./install.sh &&
cd ../mechanician_arangodb/src &&
pip install -e .

