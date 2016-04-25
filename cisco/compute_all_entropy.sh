#!/bin/bash

#ALGS=( CRC16 CRC32 MMH3 SHA256 AESGCM AESCBC SIPHASH )
ALGS=( ) # SIPHASH AESCBC SHA256 )
MAX_INDEX=22
URI_FILE=$1

for ALG in "${ALGS[@]}"
do
    index=1
    while [ $index -lt $MAX_INDEX ]
    do
        offset=1
        while [ $offset -lt $MAX_INDEX ]
        do
            OUT=${URI_FILE}_${ALG}_${index}_flatten.txt
            DATA_OUT=${URI_FILE}_${ALG}_${index}_${offset}_flatten.csv
            cmd="python ../parallel_entropy.py ${OUT} ${offset} > ${DATA_OUT}"
            echo $cmd
            eval $cmd

            if [ $? -ne 0 ]; then
                echo "FAILURE on ${OUT}"
                exit
            fi

            OUT=${URI_FILE}_${ALG}_${index}.txt
            DATA_OUT=${URI_FILE}_${ALG}_${index}_${offset}.csv
            cmd="python ../parallel_entropy.py ${OUT} ${offset} > ${DATA_OUT}"
            echo $cmd
            eval $cmd

            if [ $? -ne 0 ]; then
                echo "FAILURE on ${OUT}"
                exit
            fi

            offset=$[$offset+1]
        done
        index=$[$index+1]
    done
done

URI_FILE=$1
MAX_INDEX=22
OUT=${URI_FILE}
DATA_OUT=${OUT}_plain_21
#python ../parallel_entropy.py ${OUT} ${MAX_INDEX} > ${DATA_OUT}.out

OUT=${URI_FILE}
DATA_OUT=${OUT}_plain_flatten_21
python ../parallel_entropy.py ${OUT} ${MAX_INDEX}  > ${DATA_OUT}.out
