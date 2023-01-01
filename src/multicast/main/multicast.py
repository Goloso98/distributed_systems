import heapq
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from numpy.random import poisson, randint

import grpc
import multicast_pb2
import multicast_pb2_grpc
from google.protobuf.empty_pb2 import Empty

class MulticastService(multicast_pb2_grpc.MulticastServiceServicer):
    def __init__(self, sender):
        # Initialize the Lamport clock to 0.
        # 0 is not sent with grpc
        self.lamport_clock = 1

        # Initialize the list of peers.
        self.peers = {}

        # Initialize the sender ID.
        self.sender = sender

        # Initialize the message heap.
        self.message_heap = []

        # Load the list of peers from the JSON file.
        with open('peers.json', 'r') as f:
            self.peers = json.load(f)

        # Remove myself from the list.
        del(self.peers[sender])

    def ReceiveMessage(self, request, context):
        # Process Own Messages.
        if request.sender == self.sender:
            # Create message.
            self.lamport_clock += 1
            message = multicast_pb2.MulticastMessage(
                lamport_clock=self.lamport_clock,
                sender=self.sender,
                kind=multicast_pb2.Kind.MESSAGE,
                content=request.content
            )
            # Add to own queue to process when ready.
            heapq.heappush(self.message_heap, (message.lamport_clock, message.kind, message.sender, message))
            self.Broadcast(message)
            #context.add_callback(lambda x: self.Broadcast(message))
            return Empty()

        # Update the Lamport clock.
        self.lamport_clock = max(self.lamport_clock, request.lamport_clock)

        # Broadcast the acknowledgement message to all peers.
        if request.kind == multicast_pb2.Kind.MESSAGE:
            # Create an acknowledgement message.
            ack_message = multicast_pb2.MulticastMessage(
                lamport_clock=self.lamport_clock,
                sender=self.sender,
                kind=multicast_pb2.Kind.ACK
            )
            #context.add_callback(lambda x: self.Broadcast(ack_message))
            self.Broadcast(ack_message)

        # Print the received message.
        # print(f'[info] Received message from {request.sender} with Lamport clock {request.lamport_clock}')

        # Add the received message to the minheap.
        heapq.heappush(self.message_heap, (request.lamport_clock, request.kind, request.sender, request))
        #print("[info] heap: ", self.message_heap)

        # Check if it is time to process a new message.
        # Top of the heap has a tuple and the real message is in the 4rd possition.
        topQ_kind = self.message_heap[0][3].kind
        # check if there are any message in queue before pop any ack, instead of len
        while any(map(lambda x: x[3].kind == multicast_pb2.Kind.MESSAGE, self.message_heap)) and \
                topQ_kind == multicast_pb2.Kind.ACK:
            heapq.heappop(self.message_heap)
            topQ_kind = self.message_heap[0][3].kind

        if topQ_kind == multicast_pb2.Kind.MESSAGE:
            # Before doing anything, check if there are messages from everyone in the queue.
            queue_senders = set(map(lambda x: x[3].sender, self.message_heap))
            queue_senders.discard(self.sender)
            # If Q has messages (Ack or Message) from all other peers,
            # it is possible to dispatch the top message.
#            print("[info] before commit")
#            print("[info] sendQ", queue_senders)
#            print("[info] selfQ", self.message_heap)
            if queue_senders == set(self.peers):
                msg = heapq.heappop(self.message_heap)
                msg = msg[3]
                print(f'{msg.sender} says: {msg.content}')

        return Empty()

    def Test(self, request, context):
        self.lamport_clock = max(self.lamport_clock, request.lamport_clock) + 1
        ack_message = multicast_pb2.MulticastMessage(
            lamport_clock=self.lamport_clock,
            sender=self.sender,
            kind=multicast_pb2.Kind.Ack
        )
        time.sleep(5)
        return ack_message

    def Broadcast(self, message):
        # Broadcast message to all peers.
        for peer_id in self.peers.values():
            try:
                # Connect to the peer.
                channel = grpc.insecure_channel(peer_id)
                stub = multicast_pb2_grpc.MulticastServiceStub(channel)

                # Send the message.
                stub.ReceiveMessage(message)
            except Exception as e:
                print(f'Error sending message: {message} to peer {peer}: {e}')


def generator_of_words(mine, mine_id):
    if input("Start generating words? y/n: ") != 'y':
        return
    print("[info] start generating words")
    lam = 10  # defined in moodle
    while True:
        wait = poisson(lam)
        time.sleep(wait)
        word = fetch()
        with grpc.insecure_channel(mine_id) as channel:
            stub = multicast_pb2_grpc.MulticastServiceStub(channel)
            message = multicast_pb2.MulticastMessage(
                lamport_clock=1,
                sender=mine,
                kind=multicast_pb2.Kind.MESSAGE,
                content=word
            )
            print(f'Sending {word}...')
            response = stub.ReceiveMessage(message)

def fetch():
    with open("words.txt") as f:
        size = int(f.readline())
        rnd = randint(1, size)
        for _ in range(rnd):
            f.readline()
        word = f.readline().strip()
        return word

## ---- main
with open('peers.json', 'r') as f:
    peers = json.load(f)
#print('peers:', list(peers.keys()))
#peername = input('peer name: ')
peername = sys.argv[1]

if peername not in peers:
    sys.exit(1)

server = grpc.server(ThreadPoolExecutor(max_workers=10))
multicast_pb2_grpc.add_MulticastServiceServicer_to_server(MulticastService(peername), server)
server.add_insecure_port(peers[peername])
print(f'Running on {peername}@{peers[peername]}.')

t = threading.Thread(target=generator_of_words, daemon=True, args=(peername, peers[peername],))
t.start()

server.start()

try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)

