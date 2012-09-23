#!/bin/bash

DATA="some test data
and
more"

export OPSQUEUEDIR=/tmp/opstest/queues

mkdir -p $OPSQUEUEDIR

./objectps -v list

#echo $DATA | ssh localhost ./objectps -v spool -
echo $DATA | ./objectps -v spool -
