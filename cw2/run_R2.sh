#!/bin/bash

# $1 file being sent, for diff

while true
do
    python3 Receiver2.py 1234 test_r.jpg
    diff test_r.jpg $1
done