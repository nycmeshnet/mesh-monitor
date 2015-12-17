# nycmesh-monitor

To monitor what nodes are currently connected and when they were last seen.  

Currently the ip's in the script are for my dev setup and will need to be changed for it to work for you.

## Usage

`router_monitor.sh` is to be placed on a mesh router and configured to run at a set interval

`api.py` is a python flask server that will listen for the data and add it to a database to be viewed in a webpage.
