# Projeto_Redes
This project is intended for network design
Rodrigo Venancio
Cainã D'Ajuda

The software aims to promote a connection between multiple peers for a chat on LAN.
---------------------------------------------

PYTHON:
In python folder run:
python chatApp.py

note: If your network interface is different from eth0 is necessary to change the line 28 of the code.

EXEMPLE:
eth0 interface:
self.host_ip = (self.get_ip_address ('eth0'), 8090)

Wlan0 interface:
self.host_ip = (self.get_ip_address ('wlan0'), 8090)
---------------------------------------------

JAVA:
In java folder run:
java -jar chatApp.jar

note: OpenJDK 1.7 Required
