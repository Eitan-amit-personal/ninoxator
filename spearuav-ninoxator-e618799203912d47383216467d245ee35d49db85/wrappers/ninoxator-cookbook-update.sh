#!/usr/bin/env bash

export PYTHONPATH=$PYTHONPATH:$PWD
python flows/flow_cookbook_update.py
read -p "Done. Press Enter to quit."
