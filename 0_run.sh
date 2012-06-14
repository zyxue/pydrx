#! /bin/bash

pwd=${PWD}
yaml=${PWD}/pydr.yml

# echo ${pwd}
# echo ${yaml}

for i in 00 01 02 03; do
    cd replicas/${i}
    if [ i == 00 ]; then
	qsub run.py -v "YAML=${yaml},BIGMASTER_FLAG=1"
    else;
	qsub run.py -v "YAML=${yaml}"
    fi
    cd ${pwd}
done