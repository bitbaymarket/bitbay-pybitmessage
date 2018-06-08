#!/bin/bash
while true
do
	echo About to start/restart
	python bitbay/market_tracker.py
	sleep 1
done
