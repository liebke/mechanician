#!/bin/bash

cd ../../src &&
pip install -e . &&
cd ../examples/tmdb/src &&
cd .. && 
pip install openai &&
pip install requests
