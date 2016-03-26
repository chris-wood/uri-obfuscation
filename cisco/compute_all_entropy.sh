#!/bin/bash

ALGS=( CRC16 CRC32 MMH3 SHA256 AESGCM AESCBC SIPHASH )
MAX_INDEX=22
URI_FILE=$1

for ALG in "${ALGS[@]}"
do
    index=1
    while [ $index -lt $MAX_INDEX ]
    do
        OUT=${URI_FILE}_${ALG}_${index}_flatten.txt
        DATA_OUT=${OUT}.csv
        cmd="python ../parallel_entropy.py ${OUT} ${index} > ${DATA_OUT}"
        echo $cmd
        eval $cmd

        if [ $? -ne 0 ]; then
            echo "FAILURE on ${OUT}"
            exit
        fi

        OUT=${URI_FILE}_${ALG}_${index}.txt
        DATA_OUT=${OUT}.csv
        cmd="python ../parallel_entropy.py ${OUT} ${index} > ${DATA_OUT}"
        echo $cmd
        eval $cmd

        if [ $? -ne 0 ]; then
            echo "FAILURE on ${OUT}"
            exit
        fi

        index=$[$index+1]
    done
done
