from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Data(_message.Message):
    __slots__ = ["nullable", "text"]
    NULLABLE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    nullable: bool
    text: str
    def __init__(self, text: _Optional[str] = ..., nullable: bool = ...) -> None: ...

class Reg(_message.Message):
    __slots__ = ["ip"]
    IP_FIELD_NUMBER: _ClassVar[int]
    ip: str
    def __init__(self, ip: _Optional[str] = ...) -> None: ...

class Void(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
