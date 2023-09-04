#!/bin/bash
#execute order 66
function clean_up {

    # Perform program exit housekeeping
    kill $BGPID1
    kill $BGPID2
    kill $BGPID3
    kill $BGPID4
    exit
}
trap clean_up SIGHUP SIGINT SIGTERM
python3 rds_tx_nrsc5.py &
BGPID1=$!
./audio.sh &
BGPID2=$!
./HD1_meta.sh &
BGPID3=$!
sleep 10
python3 hd8art.py &
BGPID4=$!
wait $BGPID1 $BGPID2 $BGPID3 $BGPID4
#trap 'kill $(jobs -p)' EXIT

