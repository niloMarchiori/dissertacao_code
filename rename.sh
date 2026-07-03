#!/bin/bash

cd /home/nilo/Documents/dissertacao_code_ref/Analise/iid_all || exit 1

i=1
for f in *metrics_all.csv; do
  mv -- "$f" "metrics_iid_all_${i}.csv"
  ((i++))
done

cd -