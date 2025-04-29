#!/usr/bin/env bash

export PYTHONPATH=$PYTHONPATH:$PWD
python flows/flow_read_nfc_network_id.py
read -p "Done. Press Enter to quit."
