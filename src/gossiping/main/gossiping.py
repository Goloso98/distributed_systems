from concurrent import futures
from numpy.random import choice, poisson, random
import logging
import threading

from gossiping_pb2 import Data, Reg, Void
import gossiping_pb2_grpc
import grpc


class Gossiping(gossiping_pb2_grpc.GossipingServicer):

    def __init__(self, shared):
        self.shared = shared
        self.uri = self.shared.geturi()

    def Register(self, request, context):
        self.shared.addPeer(request.ip)
        return Void()

    def LocalRegister(self, request, context):
        with grpc.insecure_channel(request.ip) as channel:
            stub = gossiping_pb2_grpc.GossipingStub(channel)
            response = stub.Register(Reg(ip=self.uri))
        self.shared.addPeer(request.ip)
        return Void()

    def Dessiminate(self, request, context):
        print("Dessiminate", request.text)
        self.shared.addWord(request.text)
        context.add_callback(lambda: self.run(request.text))
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
            stub = gossiping_pb2_grpc.GossipingStub(channel)
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
    ip = input("ip: ")
    with grpc.insecure_channel(uri) as channel:
        stub = gossiping_pb2_grpc.GossipingStub(channel)
        response = stub.LocalRegister(Reg(ip=ip))


def serve():
    myuri = input('port(50051):')
    share = Share(myuri)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    gossiping_pb2_grpc.add_GossipingServicer_to_server(Gossiping(share), server)
    server.add_insecure_port(myuri)
    server.start()
    print("Server started, listening on " + myuri)

    for _ in range(int(input("machines quantity: "))):
        newpeer(myuri)

    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
