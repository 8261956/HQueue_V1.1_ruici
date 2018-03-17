#!/bin/bash

while :;
do
	python /home/clear/hqueue/backend/sync_fast.py $*
	sleep 5
done
