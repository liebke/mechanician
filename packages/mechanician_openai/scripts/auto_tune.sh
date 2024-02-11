#!/bin/bash

DM_DIR=$(cd ../.. && pwd)
DM_OPENAI_DIR=${DM_DIR}/packages/mechanician_openai

python3 ${DM_OPENAI_DIR}/src/mechanician_openai/instruction_auto_tuner.py
