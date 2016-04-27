#!/bin/bash

ALGS=( CRC16 CRC32 MMH3 SHA256 AESGCM AESCBC SIPHASH )
MAX_INDEX=21
URI_FILE=$1

for ALG in "${ALGS[@]}"
do
        OUT=${URI_FILE}_${ALG}_${MAX_INDEX}_flatten.txt
	DATA_OUT=${OUT}
	cmd="python ../multi.py ${OUT} ${MAX_INDEX} ${DATA_OUT}.csv > ${DATA_OUT}.out"
        echo $cmd
        eval $cmd

        if [ $? -ne 0 ]; then
            echo "FAILURE on ${OUT}"
            exit
        fi

        OUT=${URI_FILE}_${ALG}_${MAX_INDEX}.txt
	DATA_OUT=${OUT}
	cmd="python ../multi.py ${OUT} ${MAX_INDEX} ${DATA_OUT}.csv > ${DATA_OUT}.out"
        echo $cmd
        eval $cmd

        if [ $? -ne 0 ]; then
            echo "FAILURE on ${OUT}"
            exit
        fi
done
