#!/bin/bash

cd ../../packages/mechanician &&
./install.sh &&
cd ../mechanician_openai &&
./install.sh &&
cd ../mechanician_arangodb &&
./install.sh &&
cd ../../examples/arango_movie_db &&
pip install -e .
pip install -e ".[dev]"

echo "Make sure to set up your .env file, see the dot_env_example file for an example"