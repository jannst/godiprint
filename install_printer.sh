#!/bin/bash

set -e 

sudo apt update
sudo apt install -y cmake libcupsimage2-dev libcups2-dev cups

cd epson_driver
./build.sh
./install.sh
printer=$(lpinfo -v | grep usb://EPSON/TM | cut -d " " -f 2)

if [ -z "$printer" ]; then
  echo "No printer found. Make sure it is connected via USB and turned on. Exiting."
  exit 1
fi

echo Using printer ${printer}

lpadmin -v "${printer}" -p "EPS" -P "ppd/tm-ba-thermal-rastertotmtr-203.ppd" -o TmxPaperReduction=Both -o TmxPaperCut=NoCut -o PageSize=RP80x2000
cupsenable EPS && cupsaccept EPS
lpoptions -p EPS -l
echo Hello Beauty, I am your printer and I was freshly installed. | lp -d EPS


