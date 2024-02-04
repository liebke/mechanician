#!/bin/bash

EX_DIR=$(cd .. && pwd)
MECHANICIAN_TMDB_TESTS=${EX_DIR}/tmdb

python3 ${MECHANICIAN_TMDB_TESTS}/src/mechanician_tmdb/main.py
