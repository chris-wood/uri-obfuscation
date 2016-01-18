for i in `seq 1 14`; do
#    wget http://www.icn-names.net/download/datasets/cisco-icn-names-2014-12/cisco-icn-names-2014-12_${i}.txt.xz 
    xz -dc < cisco-icn-names-2014-12_${i}.txt.xz >> uris.txt
done