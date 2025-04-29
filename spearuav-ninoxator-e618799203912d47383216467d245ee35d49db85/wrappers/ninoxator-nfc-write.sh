#!/usr/bin/env bash

export PYTHONPATH=$PYTHONPATH:$PWD
python flows/flow_set_nfc_network_id.py
read -p "Done. Press Enter to quit."
