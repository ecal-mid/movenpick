# -*- coding: utf-8 -*-

from FP import Maybe, List
from os_helpers import get_directories, get_files_from_root
from feature_helpers import extract_image_features, process_image, split_data, normalize_data, normalize_data_prediction, feature_reduction
from ml_helpers import save_data, load_data, experiment, train_model, save_model, load_model, predict_with_model
from lambdas import list_to_tuple, nothing_if_empty, is_not_none, split_to_tuple, add_reducer
from decorating import animated
import argparse
import time

#### Server

#from app import im2text_pb2, im2text_pb2_grpc

import im2text_pb2_grpc
import im2text_pb2

from concurrent import futures
import time
import grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class Im2Text(im2text_pb2_grpc.Im2TxtServicer):

    def Run(self, request, context):
        fn = 'eye_lean.jpg'
        fn = request.text

        print('1')
        #with open(fn, 'wb') as file:
        #    print('2')
        #    file.write(request.image)

        print('3')
        res = 'ERROR'
        try:
            res = predict([fn])
        except Exception as e:
            print(e)

        return im2text_pb2.Im2TxtReply(text=str(res))


#### Emotion detection

# OPTIMIZATIONS TO BE DONE (hopefully)
# - Eliminate lambdas
# - Do more FP
# - Use keyword arguments

IMAGE_DIR = './images'
OLD_MODEL_PATH = './old_emotion_detector.pkl'
NEW_MODEL_PATH = './emotion_detector.pkl'
DATA_PATH = './data.pkl'
EMOTIONS = get_directories(IMAGE_DIR)

model = None

def accept_commands():
    data_arg, train_arg, predict_arg = parse_args()

    if data_arg is not None:
        generate_data(data_arg[0])

    elif train_arg is True:
        train()

    elif predict_arg is not None:
        print(predict(predict_arg))

def parse_args():
    parser = argparse.ArgumentParser(description='Emotion Detection Application')
    parser.add_argument('--train', action='store_true', help='start training the program to predict emotions')
    parser.add_argument('--data', nargs=1, help='process images from specified folder into usable data', metavar='path_to_training_folder')
    parser.add_argument('--predict', nargs='+', help='predict the emotion of face in image', metavar='path_to_input_image')
    args = parser.parse_args()
    unpacked_args = vars(args)
    data_arg = unpacked_args['data']
    train_arg = unpacked_args['train']
    predict_arg = unpacked_args['predict']

    return data_arg, train_arg, predict_arg

def generate_data(image_dir=IMAGE_DIR):
    return List.of(get_directories(image_dir)) \
        .chain(get_files_from_root(image_dir)) \
        .reduce(add_reducer) \
        .map(extract_image_features) \
        .reduce(split_data, ([], [])) \
        .map(normalize_data) \
        .map(feature_reduction(OLD_MODEL_PATH, True)) \
        .map(split_to_tuple) \
        .map(save_data) \
        .value


@animated
def train(data_dir=DATA_PATH):
    print("Training start...")

    Maybe.of(load_data()) \
        .map(experiment) \
        .map(train_model) \
        .map(save_model)

    print("Training complete.")


def predict(image_paths):
    print("Predicting...")
    print(image_paths)
    # get the time of a prediction

    t = time.process_time()
    preprocess = List(image_paths) \
        .map(process_image) \
        .filter(is_not_none) \
        .fold(nothing_if_empty) \
        .reduce(list_to_tuple, ())

    elapsed_time = time.process_time() - t
    print("Preprocessing time {}".format(elapsed_time))

    t = time.process_time()

    result = preprocess \
        .map(normalize_data_prediction) \
        .map(feature_reduction(OLD_MODEL_PATH)) \
        .map(predict_with_model(model)) \
        .map(get_emotions) \
        .value

    print("Prediction time {}".format(elapsed_time))
    elapsed_time = time.process_time() - t

    return result

# Remove DS Store from images: rm ./app/images/*/.DS_Store


def get_emotions(emotion_indices):
    return [EMOTIONS[index] for index in emotion_indices]


def init():
    """Sets up things we only need to do once"""
    print("Loaded model")
    global model
    model = load_model()


def serve():
    print("Serving started")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    im2text_pb2_grpc.add_Im2TxtServicer_to_server(Im2Text(), server)
    server.add_insecure_port('[::]:50051')
    server.start()

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    init()
    accept_commands()
    print(model)
    serve()

