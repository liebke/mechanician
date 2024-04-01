#!/bin/bash

cd ./src
# uvicorn mechanician_studio.app:app --reload
uvicorn studio_demo.main:app --reload
