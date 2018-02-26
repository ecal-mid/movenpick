from __future__ import print_function

import serial
import grpc
import threading

from im2text_pb2 import *
from im2text_pb2_grpc import *

import cv2
from gtts import gTTS
import subprocess
import glob
import sys
import time
import datetime

btn_clicked = False

def serial_ports():
	if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
	        # this excludes your current terminal "/dev/tty"
	        ports = glob.glob('/dev/tty[A-Za-z]*')

	result = []
	portArduino = ""
	for port in ports:
	    try:
	        s = serial.Serial(port)
	        s.close()
	        result.append(port)
	        if port.find("ACM") != -1:
	        	portArduino = port
	    except (OSError, serial.SerialException):
	        pass
	    return portArduino

#todo
#ser = serial.Serial(serial_ports())

def run():
    running = 1
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("test")

    channel = grpc.insecure_channel('localhost:50051')
    #stub = im2txt_pb2_grpc.Im2TxtStub(channel)

    tmp_jpg_filename = 'img'
    tmp_mp3_filename = '_mp3_tmp.wav'

    while running == 1:
        try :
            ret, frame = cam.read()
            cv2.imshow("test", frame)

            if not ret:
                break

            k = cv2.waitKey(1)
            if 's' == chr(k & 255):
                print("send image to docker")

                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')

                fn = 'temp_' + st + '.jpg'
                cv2.imwrite(fn, frame)

                with open(fn, 'r') as f:
                    imageTo = f.read()

                # create stub etc ...

            #todo - send image to docker
            #print("Send image to docker")
#            if ser.inWaiting() > 0:
#                line = ser.read(ser.inWaiting()).decode('ascii')
#
#                print(line, end='')
#                if len(line) > 0:
#                    print("Started recognition")
#
                    # ts = time.time()
                    # st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')
                    #
                    # cv2.imwrite(tmp_jpg_filename+"_"+st+".jpg", frame)
                    # with open(tmp_jpg_filename+"_"+st+".jpg", "r") as f:
                    #      imageTo = f.read()
                    # response = stub.Run(im2txt_pb2.Im2TxtRequest(image=imageTo))
                    # print("Response received: " + response.text)
                    #
                    # tts = gTTS(text=response.text, lang='en')
                    #
                    # tts.save(tmp_mp3_filename)
                    # subprocess.Popen(['mpg123', tmp_mp3_filename]).wait()
               
            
        except KeyboardInterrupt:
            running = 0
            print("Session ended")
            ser.close()

        
    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("hi")
    run()

