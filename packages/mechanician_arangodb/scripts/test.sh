#!/bin/bash

PKG_DIR=$(cd .. && pwd)
echo $PKG_DIR

MECHANICIAN_CORE_SRC=${PKG_DIR}/mechanician_core/src
MECHANICIAN_OPENAI_SRC=${PKG_DIR}/mechanician_openai/src
MECHANICIAN_ARANGODB_SRC=${PKG_DIR}/mechanician_arangodb/src
MECHANICIAN_ARANGODB_TESTS=${PKG_DIR}/mechanician_arangodb/tests/mechanician_arangodb

echo "python3 ${MECHANICIAN_ARANGODB_TESTS}/test_ai.py"

python3 ${MECHANICIAN_ARANGODB_TESTS}/test_ai.py
