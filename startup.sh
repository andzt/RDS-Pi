#!/bin/sh
# startup.sh
# navigate to home directory, then to this directory, then execute python script, then back home

## uncomment to force update on next reboot...
#sudo apt-get update
#sudo apt-get upgrade

### Update and run code files
cd /home/pi/pirds
sleep 60
sudo git pull
sleep 20
sudo python manager.py
cd /