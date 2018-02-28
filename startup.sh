# Startup script

# Start docker server

# Interactive mode - use for debugging
#docker run -v /home/ecal-mid/mudac/movenpick/app:/home/app -p 50051:50051 -it --net=host  mudac-emotion

docker run -v /home/ecal-mid/mudac/movenpick/app:/home/app -p 50051:50051 -d --net=host  mudac-emotion /home/app/start_server.sh

# Start webcam client

# Start image watchdog

# Start image server