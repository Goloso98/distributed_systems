from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

ACK: Kind
DEFAULT: Kind
DESCRIPTOR: _descriptor.FileDescriptor
MESSAGE: Kind

class MulticastMessage(_message.Message):
    __slots__ = ["content", "kind", "lamport_clock", "sender"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    LAMPORT_CLOCK_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    content: str
    kind: Kind
    lamport_clock: int
    sender: str
    def __init__(self, lamport_clock: _Optional[int] = ..., sender: _Optional[str] = ..., kind: _Optional[_Union[Kind, str]] = ..., content: _Optional[str] = ...) -> None: ...

class Kind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
