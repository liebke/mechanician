#/bin/bash

cd ../../src &&
pip install -e . &&
cd ../examples/tmdb &&
pip install openai &&
pip install requests
