$(foreach ($i in 1..88) {
    Write-Host "Fetching $i"
    Invoke-WebRequest http://www.icn-names.net/download/datasets/unibas-url-names-2014-08-unique/unibas-url-names-2014-08-unique_$i.txt.xz
})