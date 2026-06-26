#!/bin/bash

cd /home/nilo/Documents/dissertacao_code_calibrar_const/Analise/calibrar_alpha_2 || exit 1

i=1
for f in *_calibrar_alpha.csv; do
  mv -- "$f" "calibrar_alpha_${i}.csv"
  ((i++))
done