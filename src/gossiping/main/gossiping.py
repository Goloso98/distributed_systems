from concurrent import futures
from numpy.random import choice, poisson, random, randint
from time import sleep
import json
import logging
import sys
import threading

from gossiping_pb2 import Data, Reg, Void
import gossiping_pb2_grpc as rpc
import grpc


class Gossiping(rpc.GossipingServicer):

    def __init__(self, shared):
        self.shared = shared
        self.uri = self.shared.geturi()

    def Register(self, request, context):
        self.shared.addPeer(request.ip)
        return Void()

    def LocalRegister(self, request, context):
        with grpc.insecure_channel(request.ip) as channel:
            stub = rpc.GossipingStub(channel)
            response = stub.Register(Reg(ip=self.uri))
        self.shared.addPeer(request.ip)
        return Void()

    def Dessiminate(self, request, context):
        print("Dessiminate", request.text)
        self.shared.addWord(request.text)
        #context.add_callback(lambda: self.run(request.text))
        # Schedule the run method to be run asynchronously
        t = threading.Thread(target=self.run, args=(request.text,))
        t.start()
        return Void()

    def run(self, word):
        print("run")
        if self.shared.getWord(word) > 0:
            k = 1.5
            p = 1/k
            rnd = random()
            if rnd > p:
                print("stop")
                return
        peer = self.shared.getrand()
        print("choose", peer)
        with grpc.insecure_channel(peer) as channel:
            stub = rpc.GossipingStub(channel)
            response = stub.Dessiminate(Data(text=word))
        print("Sent", peer, word)


class Share(object):
    
    def __init__(self, uri):
        self.words = {}  # { "word": number of uses }
        self.peers = set()
        self.uri = uri

    def geturi(self):
        return self.uri

    def getrand(self):
        return choice(tuple(self.peers))

    def addPeer(self, peerip):
        self.peers.add(peerip)
        print("add")

    def addWord(self, word):
        if word in self.words:
            self.words[word] += 1
        else:
            self.words[word] = 0

    def getWord(self, word):
        return self.words[word]


def newpeer(uri):
    with open("machines.txt") as f:
        machines = json.load(f)
    print("machines: ", list(machines.keys()))
    ip = input('peer ip: ')
    if ip in machines:
        ip = machines[ip]
    else:
        print("nao encontrado")
        sys.exit(1)
    with grpc.insecure_channel(uri) as channel:
        stub = rpc.GossipingStub(channel)
        response = stub.LocalRegister(Reg(ip=ip))


def appendwords(uri):
    lam = 30  # defined in moodle
    while True:
        wait = poisson(lam)
        sleep(wait)
        word = fetch()
        with grpc.insecure_channel(uri) as channel:
            stub = rpc.GossipingStub(channel)
            response = stub.Dessiminate(Data(text=word))

def fetch():
    with open("words.txt") as f:
        size = int(f.readline())
        rnd = randint(1, size)
        for _ in range(rnd):
            f.readline()
        word = f.readline().strip()
        return word


def serve():
    with open("machines.txt") as f:
        machines = json.load(f)
    print("machines: ", list(machines.keys()))
    myuri = input('meu ip: ')
    if myuri in machines:
        myuri = machines[myuri]
    else:
        print("nao encontrado")
        sys.exit(1)
    share = Share(myuri)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    rpc.add_GossipingServicer_to_server(Gossiping(share), server)
    server.add_insecure_port(myuri)
    server.start()
    print("Server started, listening on " + myuri)

    for _ in range(int(input("machines quantity: "))):
        newpeer(myuri)

    t = threading.Thread(target=appendwords, args=(myuri,))
    t.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
