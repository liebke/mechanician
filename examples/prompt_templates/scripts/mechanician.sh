#!/bin/bash

cd ./src
# uvicorn mechanician_ui.app:app --reload
uvicorn prompt_templates.main:app --reload
