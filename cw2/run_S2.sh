#!/bin/bash

#$1 is the file name

params=(5 10 15 20 25 30 40 50 75 100)

for i in {0..9}
do
    for j in {0..4}
    do
        python3 Sender2.py localhost 1234 $1 ${params[$i]}
        sleep 1s
    done
    echo ""
done
