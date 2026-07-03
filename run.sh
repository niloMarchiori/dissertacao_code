#!/bin/bash

# Script to run calibrar_alpha.py 5 times sequentially with mnf_clean between runs
# Execute with: sudo -E ./run_calibrar_5times.sh

for i in {1..1}; do
    echo "=========================================="
    echo "Running iteration $i of 5..."
    echo "=========================================="
    mnf_clean
    sleep 2
    python topology_afea/non_iid_afea.py
done

echo "=========================================="
echo "All 5 iterations completed!"
echo "=========================================="
