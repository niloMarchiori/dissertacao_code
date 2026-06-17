#!/bin/bash

# Script to run calibrar_alpha.py 5 times sequentially with mnf_clean between runs
# Execute with: sudo -E ./run_calibrar_5times.sh

for i in {1..5}; do
    echo "=========================================="
    echo "Running iteration $i of 5..."
    echo "=========================================="
    mnf_clean
    python calibrar_const/calibrar_alpha.py
    
    if [ $i -lt 5 ]; then
        echo "Cleaning up with mnf_clean..."
        mnf_clean
        echo "Cleanup complete. Waiting before next iteration..."
        sleep 2
    fi
done

echo "=========================================="
echo "All 5 iterations completed!"
echo "=========================================="
