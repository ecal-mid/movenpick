#!/usr/bin/env bash
# Startup script

# Start docker server

# Interactive mode - use for debugging
#docker run -v /home/ecal-mid/mudac/movenpick/app:/home/app -p 50051:50051 -it --net=host  mudac-emotion
#docker run -v /home/ecal-mid/mudac/movenpick/app:/home/app -p 50051:50051 --net=host -it

docker run -v /home/ecal-mid/mudac/movenpick/app:/home/app -p 50051:50051 --net=host -d --entrypoint "/home/app/start_server.sh" mudac-emotion

# Start webcam client and write logs
cd /home/ecal-mid/mudac/movenpick/app
python -u /home/ecal-mid/mudac/movenpick/app/webcam_client.py > /home/ecal-mid/mudac/movenpick/app/webcam.log 2>&1 &

# Start image watchdog
cd /home/ecal-mid/mudac/movenpick/app/imageServer/movenpick/
python -u watcher.py images > /dev/null &

# Start image server
cd /home/ecal-mid/mudac/movenpick/app/imageServer/movenpick/
python -m SimpleHTTPServer 8888 &