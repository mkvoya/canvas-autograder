#!/bin/sh

for i in $(seq 1 1000); do
    echo "Test round $i"
    date
    python3 auto.py
    date
    echo "Waiting for next round..."
    sleep 1800
done
