from __future__ import print_function
from shutil import copyfile
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
import signal



print('Starting webcam client')

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
        print(portArduino)
        return portArduino


current_emotion = "unknown"
previous_emotion = "unknown"

ser = serial.Serial(serial_ports())

current_arduino_emotion = 'sad'
dict_arduino_emotion = {2: 'angry', 3: 'sad', 4: 'happy'}
cam = None



def get_arduino_emotion(n):
    try:
        return dict_arduino_emotion[n]
    except Exception:
        return 'error'

def run():
    global future_emotion
    global current_emotion
    global previous_emotion
    global current_arduino_emotion
    global cam

    running = 1
    cam = cv2.VideoCapture(0)
    cam.set(3, 1920)
    cam.set(4, 1080)

    cv2.namedWindow("test")

    channel = grpc.insecure_channel('localhost:50051')
    stub = Im2TxtStub(channel)

    while running == 1:
        try:

            ret, framefull = cam.read()
            #print(frame.shape)
            cv2.imshow("test", framefull)

            frame = imutils.resize(framefull, width=500)

            try:
                if ser.inWaiting() > 0:
                    line = ser.read(ser.inWaiting()).decode('ascii')
                    print(line, end='')
                    current_arduino_emotion = get_arduino_emotion(int(line))
                    print('current emotion {}'.format(current_arduino_emotion))
            except Exception as e:
                print(e)
                current_emotion = 'error'

            if not ret:
                break

            k = cv2.waitKey(1)

            if future_emotion is None or future_emotion.done():


                if future_emotion is not None:
                    current_emotion = future_emotion.result().text
                    print(current_emotion)
                    if previous_emotion != current_emotion and current_emotion != 'unknown':
                        if current_emotion == current_arduino_emotion:
                            print('img saved')
                            ts = time.time()
                            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
                            new_fn = st + '_' + current_emotion + '.jpg'
                            copyfile(full_filename, 'ipad_server/' + new_fn)

                    previous_emotion = current_emotion

                fn = 'temp_analysis.jpg'
                full_filename = 'large.jpg'
                #frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cv2.imwrite(fn, frame)
                cv2.imwrite(full_filename, framefull)
                future_emotion = pool.submit(get_emotion, fn, stub)

        except KeyboardInterrupt:
            running = 0
            print("Session ended")
            ser.close()

    cam.release()
    cv2.destroyAllWindows()


def handle_exit():
    print("Kill signal detected, cleaning up ...")
    global cam
    global ser

    cam.release()
    ser.close()


signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

if __name__ == "__main__":
    print("Starting webcam client ...")
    try:
        run()
    except Exception as e:
        print("STOPPING BECAUSE OF ERROR")
        cam.release()
        ser.close()
        print(e)
        exit()
