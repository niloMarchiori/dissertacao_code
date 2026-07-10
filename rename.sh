#!/bin/bash

cd ./Analise/non_iid_afea || exit 1

i=1
for f in *_metrics_afea.csv; do
  mv -- "$f" "metrics_non_iid_afea_${i}.csv"
  ((i++))
done

cd -