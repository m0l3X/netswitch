# netswitch
A simple solution for switching over your own home network devices from outer world.

Wake-On-Lan reimagined
<hr>
Netswitch allows to turn on/off your home network devices via simple syntax and memorable keywords.


## Requirements

> Python >=3.10
> 
yep it is built on simple python tho..

## Usage

First, you need a IoT device that stays always on, an old phone or raspberry py would work - this'll be a 'handler' device

Handler will listen for incoming connections and operate with devices on the same network via nettable.json file.

Handler also has an optional network password in nettable.json, which should be provided by client to be able to operate with net.

Run the handler.py script on it, and forward port 11250 to WAN (configurable in python file).

Any device running an 'endpoint' script listens for incoming connections from network's handler on port 11251.

Each 'endpoint' device has a assigned 'keyword' to it (you can change it in the python file it too), which is used to be identified for the handler.

Don't forget to add/change firewall rule on 'endpoint' devices!

<hr>
On client (netswitch.py), run in terminal: 

### netswitch [network ip] [network password (if exists)] [command] [device keyword]

Avaiable commands: 
> status - Prints out endpoint device's status information, such as local IP and mac address and adds it to nettable.json

> shut - Turns off endpoint device

> wake - Turns on endpoint device, if it was previously status'ed

> wakemac - Turns on device on network with specified MAC address

<hr>
Why did i make this?

I just was bored to manually SSH into my home phone and run another WOL script to wake my server, so i made this utility that just simplifies my life a bit.
