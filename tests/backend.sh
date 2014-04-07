#!/bin/bash

set -e

REPO=`git rev-parse --show-toplevel`

source "${REPO}/config/matterq.conf"

PATH="${REPO}/scripts:${REPO}/austerusG:${PATH}"

MQ_TESTMODE=1
MQ_DEBUG=1
MQ_SPOOLDIR=/tmp/spoolmq
#SPOOL_DIR=/tmp/spoollpr
SPOOL_DIR=""
PRINTCAP_ENTRY=""

TEST_OUTPUT=/tmp/mqtest

export PATH
export MQ_TESTMODE
export MQ_PLANNER_MODE
export MQ_SPOOLDIR
export MQ_HEADSIZE
export MQ_PRINTBED
export MQ_DEBUG
export SPOOL_DIR
export PRINTCAP_ENTRY

#mkdir -p $SPOOL_DIR
mkdir -p $MQ_SPOOLDIR/depositions
mkdir -p $MQ_SPOOLDIR/images
mkdir -p $TEST_OUTPUT

rm -f $TEST_OUTPUT/*
rm -f $MQ_SPOOLDIR/depositions/*
rm -f $MQ_SPOOLDIR/images/*

declare -i TALLY=0


while [ $# -ne 0 ]
do
    DATAFILES=$1
    export DATAFILES
    echo "JOB START: $DATAFILES"

    set +e
    matterq-lprng
    RC=$?
    set -e

    echo "JOB EXIT $RC"

    mv $MQ_SPOOLDIR/images/current.svg $TEST_OUTPUT/out-$TALLY.svg

    if [ "$RC" -eq 2 ]
    then
        echo "abort"
        exit 1
    fi

    let TALLY=$TALLY+1
    shift
done


