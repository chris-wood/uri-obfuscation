#!/bin/bash
URI_FILE=$1
MAX_INDEX=21
OUT=${URI_FILE}
DATA_OUT=OUT_plain_21
python ../multi.py ${OUT} ${MAX_INDEX} ${DATA_OUT}.csv > ${DATA_OUT}.out

OUT=${URI_FILE}
DATA_OUT=OUT_plain_flatten_21
python ../multi.py -f ${OUT} ${MAX_INDEX} ${DATA_OUT}.csv > ${DATA_OUT}.out
