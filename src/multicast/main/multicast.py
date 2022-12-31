import heapq
import sys
import json
import time
from concurrent.futures import ThreadPoolExecutor

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
            heapq.heappush(self.message_heap, (message.lamport_clock, message.kind, message))
            self.Broadcast(message)
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
            self.Broadcast(ack_message)

        # Print the received message.
        print(f'[info] Received message from {request.sender} with Lamport clock {request.lamport_clock}')

        # Add the received message to the minheap.
        heapq.heappush(self.message_heap, (request.lamport_clock, request.kind, request))

        # Check if it is time to process a new message.
        # Top of the heap has a tuple and the real message is in the 3rd possition.
        topQ_kind = self.message_heap[0][2].kind

        # Discard Ack Messages from the heap.
        if topQ_kind == multicast_pb2.Kind.ACK:
            heapq.heappop(self.message_heap)
        elif topQ_kind == multicast_pb2.Kind.MESSAGE:
            # Before doing anything, check if there are messages from everyone in the queue.
            queue_senders = set(map(lambda x: x[2].sender, self.message_heap))
            queue_senders.discard(self.sender)
            # If Q has messages (Ack or Message) from all other peers,
            # it is possible to dispatch the top message.
            if queue_senders == set(self.peers):
                msg = heapq.heappop(self.message_heap)
                msg = msg[2]
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
        for peer in self.peers:
            try:
                # Connect to the peer.
                channel = grpc.insecure_channel(self.peers[peer])
                stub = multicast_pb2_grpc.MulticastServiceStub(channel)

                # Send the message.
                stub.ReceiveMessage(message)
            except Exception as e:
                print(f'Error sending message to peer {peer}: {e}')



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
print("running")
server.start()

try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)

