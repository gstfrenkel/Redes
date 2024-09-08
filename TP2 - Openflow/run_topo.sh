#!/usr/bin/env bash

if [ -z "$1" ]; then
  echo "Uso: ./run_topo.sh <cantidad_switchs>"
else
  # Verifica si el parámetro es un número (1 ó más dígitos)
  if [[ "$1" =~ ^[1-9]+$ ]]; then
    sudo mn --custom topology.py --topo customTopo,switches_number=$1 --mac --switch ovsk --controller remote,port=6633
  else
    echo "La cantidad de switchs debe ser mayor ó igual a 1."
  fi
fi