#!/bin/sh
# launcher.sh
# navigate to root directory, then to this directory, then execute python script, then back home

cd /
cd home/pi/sources/rpi-rgb-led-matrix
sudo python jenkins.py
cd /
