from __future__ import print_function

import serial
import grpc
import threading

from im2text_pb2 import *
from im2text_pb2_grpc import *
import imutils

import cv2
from gtts import gTTS
import subprocess
import glob
import sys
import time
import datetime
import threading


from concurrent.futures import ThreadPoolExecutor

pool = ThreadPoolExecutor()
future_emotion = None

def get_emotion(filename, stub):
    #print("Send filename to docker")
    response = stub.Run(Im2TxtRequest(text=filename))
    #print(response)
    return response


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


current_emotion = "unknown"
previous_emotion = "unknown"

# todo
# ser = serial.Serial(serial_ports())

# todo
# get the current emotion
# if the current emotion is the one selected then take a picture


def run():
    global future_emotion
    global current_emotion
    global previous_emotion

    running = 1
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("test")

    channel = grpc.insecure_channel('localhost:50051')
    stub = Im2TxtStub(channel)

    while running == 1:
        try:
            ret, frame = cam.read()
            frame = imutils.resize(frame, width=500)
            cv2.imshow("test", frame)

            if not ret:
                break

            k = cv2.waitKey(1)

            if future_emotion is None or future_emotion.done():
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

                fn = 'temp_' + st + '.jpg'
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cv2.imwrite(fn, frame_rgb)

                if future_emotion is not None:
                    current_emotion = future_emotion.result().text
                    print(current_emotion)
                    #print('{}\r'.format(current_emotion), end="\r")
                    if previous_emotion != current_emotion:
                        print('Emotion has changed')
                        #todo - if emotion the same as arduino emotion send emotion to ipad

                    previous_emotion = current_emotion
                future_emotion = pool.submit(get_emotion, fn, stub)

        except KeyboardInterrupt:
            running = 0
            print("Session ended")
            ser.close()

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("hi")
    run()
