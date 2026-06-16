#!/bin/bash

# Loop from 1 to 35
for i in {25..30}; do
    # Run the Python script with the current value of pgnum
    python3 svgif.py -i ./iran_slides_1.pdf --pgnm "$i"
done
