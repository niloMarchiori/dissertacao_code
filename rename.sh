#!/bin/bash

cd /home/nilo/Documents/dissertacao_code_calibrar_constantes/Results/calibrar_alpha || exit 1

i=6
for f in *_calibrar_alpha.csv; do
  mv -- "$f" "calibrar_alpha_${i}.csv"
  ((i++))
done