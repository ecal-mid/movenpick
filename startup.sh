# Startup script

# Start docker server

# Interactive mode - use for debugging
#docker run -v /home/ecal-mid/mudac/movenpick/app:/home/app -p 50051:50051 -it --net=host  mudac-emotion

docker run -v /home/ecal-mid/mudac/movenpick/app:/home/app -p 50051:50051 --net=host -t --entrypoint "/home/app/start_server.sh" mudac-emotion

# Start webcam client and write logs
python -u /home/ecal-mid/mudac/movenpick/app/webcam_client.py > /home/ecal-mid/mudac/movenpick/app/webcam.log 2>&1 &

# Start image watchdog



# Start image server