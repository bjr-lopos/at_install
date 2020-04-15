#!/bin/bash
sudo service loposcore stop
sudo systemctl disable loposcore.service
sudo rm /etc/systemd/system/loposcore.service 
sudo rm -rf  /usr/local/bin/loposcore 
sudo apt-get --purge remove mysql-server

