#!/bin/bash

cd ../../packages/mechanician &&
./scripts/install.sh &&
cd ../mechanician_openai &&
./scripts/install.sh &&
cd ../mechanician_studio &&
./scripts/install.sh &&
cd ../mechanician_arangodb &&
./scripts/install.sh &&
cd ../mechanician_chroma &&
./scripts/install.sh &&
cd ../../examples/studio_demo &&
pip install -e .

echo "Make sure to set up your .env file, see the dot_env_example file for an example"