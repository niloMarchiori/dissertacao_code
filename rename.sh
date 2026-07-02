#!/bin/bash

cd /home/nilo/Documents/dissertacao_code_ref/Results/iid_leastEnergy || exit 1

i=1
for f in *_leastEnergy_all.csv; do
  mv -- "$f" "metrics_iid_leastEnergy_${i}.csv"
  ((i++))
done

cd -