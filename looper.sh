#!/bin/bash

# Loop from 1 to 35
for i in {1..35}; do
    # Run the Python script with the current value of pgnum
    python3 svgif.py -i ./math0.pdf --pgnm "$i" --svg
done
