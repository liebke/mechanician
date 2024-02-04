#!/bin/bash

EX_DIR=$(cd .. && pwd)
MECHANICIAN_TMDB_TESTS=${EX_DIR}/tmdb/src/mechanician_tmdb

python3 ${MECHANICIAN_TMDB_TESTS}/main.py
