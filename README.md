# Distributed Systems

## Description

This project is a collection of algorithms for communication in distributed systems. It includes a token ring program that uses a logical ring topology to pass messages to provide exclusive resource access to nodes in the system, a gossiping program to disseminate information throughout a network, and a multicast program which implements totally ordered multicast with Lamport clocks to timestamp the messages through a chat application. These algorithms are designed to be scalable, making them suitable for use in large, distributed systems.

## Prerequisites

`Python3` should be installed along with `requirements.txt`.
To install requirements `pip install -r requirements.txt`.

Generating grpc files is not needed, since they are bundled, but it can be done installing the `requirements_dev.txt` like before.
Then run the compile script found inside each program folder.

## Usage

Each individual task can be found inside `src` folder.
Here you can found the `compile_proto.sh` if you wish to do so.
Then navigate to `main` and follow the correct use case.

### Tokenring

Start by changing the file `machines.txt` to your needs and start the program `python tokenring.py`, in all nodes.
After that you will be prompted to insert the peer name, and next peer name, you should use those declared inside `machines.txt`.

When all nodes are setup, you can start by typing `start`. The commands `lock` and `unlock` are also available.

### Gossiping

First don't forget to change `machines.txt`, in all nodes, then run `python gossiping.py`.
In order to create the network, you start with the node name, then state how many nodes you will add, and then the node names one by one.

### Multicast

Again change the `peers.json`, in all nodes, then run `python gossiping.py <node_name>`. After that you need to start or ignore the generation of messages.

## Notes

 - There are some connections that triggers a TCP RESET.
 - Graceful shutdown should be implemented.
 - Async/wait to dispatch messages upon receive.
