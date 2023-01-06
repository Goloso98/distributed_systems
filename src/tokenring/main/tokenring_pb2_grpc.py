# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import tokenring_pb2 as tokenring__pb2


class TokenringStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Ring = channel.unary_unary(
                '/tokenring.Tokenring/Ring',
                request_serializer=tokenring__pb2.Token.SerializeToString,
                response_deserializer=tokenring__pb2.Void.FromString,
                )


class TokenringServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Ring(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TokenringServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Ring': grpc.unary_unary_rpc_method_handler(
                    servicer.Ring,
                    request_deserializer=tokenring__pb2.Token.FromString,
                    response_serializer=tokenring__pb2.Void.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'tokenring.Tokenring', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Tokenring(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Ring(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tokenring.Tokenring/Ring',
            tokenring__pb2.Token.SerializeToString,
            tokenring__pb2.Void.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)