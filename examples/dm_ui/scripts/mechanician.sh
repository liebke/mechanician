#!/bin/bash

cd ./src
# uvicorn mechanician_ui.app:app --reload
uvicorn dm_ui.main:app --reload
