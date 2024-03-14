#!/bin/bash

cd ./src
uvicorn mechanician_ui.app:app --reload
