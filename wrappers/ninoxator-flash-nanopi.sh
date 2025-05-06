#!/usr/bin/env bash

export PYTHONPATH=$PYTHONPATH:$PWD
python flows/flow_flash_blank_nanopi.py
read -p "Done. Press Enter to quit."
