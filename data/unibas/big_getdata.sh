for i in `seq 1 88`; do
    echo -n "Fetching ${i}...\r\c"
    wget http://www.icn-names.net/download/datasets/unibas-url-names-2014-08-unique/unibas-url-names-2014-08-unique_${i}.txt.xz
    #xz -dc < unibas-url-names-2014-08-unique_${i}.txt.xz >> uris.txt
    #sleep 1
done