#!/bin/bash

EX_DIR=$(cd .. && pwd)
OFFER_MGMT_EX=${EX_DIR}/offer_management_assistant

python3 ${OFFER_MGMT_EX}/tests/offer_mgmt/test.py
