from concurrent import futures
import concurrent.futures
from time import sleep
import json
import asyncio
import logging
import sys
import threading

import grpc
from tokenring_pb2 import Token, Void
import tokenring_pb2_grpc


class Tokenring(tokenring_pb2_grpc.TokenringServicer):

    def __init__(self, uri, lock):
        self.token = 0
        self.uri = uri
        self.lock = lock
    
    def Ring(self, request, context):
        self.token = request.num
        self.token += 1
        print(f"Token: {str(self.token)}.")
        # Schedule the run method to be run asynchronously
        t = threading.Thread(target=self.run)
        t.start()
        #print("Token reply")
        return Void()

    def run(self):
        sleep(1)
        while self.lock.getter() == True:
            sleep(0.2)
        #print("Token 1st..." + str(self.token))
        with grpc.insecure_channel(self.uri) as channel:
            stub = tokenring_pb2_grpc.TokenringStub(channel)
            response = stub.Ring(Token(num=self.token))
        #print("Greeter client received")


class Lock(object):
    
    def __init__(self):
        self.lock = False
        
    def toggle(self):
        self.lock = not self.lock
    
    def lock(self):
        self.lock = True
        print("1 locked")
    
    def unlock(self):
        self.lock = False
        print("2 unlocked")
    
    def setter(self, status):
        self.lock = status
        print("new status " + str(self.lock))
    
    def getter(self):
        return self.lock


class KeyboardThread(threading.Thread):

    def __init__(self, uri, lock):
        self.lock = lock
        self.uri = uri
        threading.Thread.__init__(self)

        self.start()
    
    def run(self):
        while True:
            inp = input()
            if inp == 'lock':
                self.lock.setter(True)
            elif inp == 'unlock':
                self.lock.setter(False)
            elif inp == 'start':
                with grpc.insecure_channel(self.uri) as channel:
                    stub = tokenring_pb2_grpc.TokenringStub(channel)
                    response = stub.Ring(Token(num=0))


def serve():
    with open("machines.txt") as f:
        machines = json.load(f)
    print("machines: ", list(machines.keys()))
    myuri = input("meu ip: ")
    if myuri in machines:
        myuri = machines[myuri]
    else:
        print("nao encontrado")
        sys.exit(1)
    nexturi = input("proximo ip: ")
    if nexturi in machines:
        nexturi = machines[nexturi]
    else:
        print("nao encontrado")
        sys.exit(1)
    lock = Lock()
    keyboard = KeyboardThread(myuri, lock)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    tokenring_pb2_grpc.add_TokenringServicer_to_server(Tokenring(nexturi, lock), server)
    server.add_insecure_port(myuri)
    server.start()
    print("Server started, listening on " + myuri)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
