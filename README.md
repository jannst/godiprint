# GodjePrint 
This is a Photobooth application designed to directly print on Epson Thermal Printers.

<div style="display:flex; margin-bottom:5px">
<img src="resources/front.jpg" width="49%">
<img src="resources/back.jpg" width="49%" style="margin-left: 5px">
</div>
![Use Case](resources/use_case.gif)

### Setup
  1. Setup a SD-Card with Raspian OS
  2. Copy contents of this repository to the device
  3. Run the `install.sh` script inside this repository on the Raspberry Pi using sudo!
  4. Run the `install_printer.sh` script inside this repository on the Raspberry Pi using sudo!


### Debugging
To follow application log use
```
sudo journalctl -fu gprint.service
```
