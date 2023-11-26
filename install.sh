#!/bin/bash

set -e 

sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pip python3-picamera2 libopenjp2-7

python3 -m pip install --upgrade evdev Pillow

echo copy boot config.txt
cp ./config.txt /boot/config.txt

echo change kernel command line
# FYI: This will rotate the screen
echo -e "video=HDMI-A-1:800x480M@59,rotate=270 $(cat /boot/cmdline.txt)" > /boot/cmdline.txt

echo install Systemd service
WORKDIR=$(pwd) envsubst < gprint.service > /etc/systemd/system/gprint.service
systemctl daemon-reload
systemctl enable gprint.service

echo Done. You may reboot your system now!