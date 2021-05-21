#!/bin/bash
cd /data/home/nao/naoqi/app/naorobotWebControl/
python videoserver.py & disown
python webSocketServer.py & disown
python httpServer.py & disown
