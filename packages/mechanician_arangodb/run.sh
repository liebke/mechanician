#!/bin/bash

PKG_DIR=$(cd .. && pwd)
MECHANICIAN_ARANGODB_TESTS=${PKG_DIR}/mechanician_arangodb/tests/mechanician_arangodb

python3 ${MECHANICIAN_ARANGODB_TESTS}/main.py
