#!/bin/bash

EX_DIR=$(cd .. && pwd)
MECHANICIAN_ARANGODB_TESTS=${EX_DIR}/arango_movie_db

python3 ${MECHANICIAN_ARANGODB_TESTS}/src/tuner.py
