# Tests receiving images from the webcam

import im2text_pb2_grpc
import im2text_pb2

from concurrent import futures
import time
import grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Im2Text(im2text_pb2_grpc.Im2TxtServicer):

    def Run(self, request, context):
        return im2text_pb2.Im2TxtReply(text="Test")


def serve():
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
    serve()
