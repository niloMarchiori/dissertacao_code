#!/bin/bash

cd /home/nilo/Documents/dissertacao_code_calibrar_const/Results/calibrar_cn || exit 1

i=6
for f in *_calibrar_cn.csv; do
  mv -- "$f" "calibrar_cn_${i}.csv"
  ((i++))
done