#!/bin/bash

EX_DIR=$(cd .. && pwd)
ARANGO_MOVIE_DB_EX_DIR=${EX_DIR}/arango_movie_db

python3 ${ARANGO_MOVIE_DB_EX_DIR}/src/test_ai.py
