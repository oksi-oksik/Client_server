from typing import TypeVar, Any, Type
from google.protobuf.internal.decoder import _DecodeVarint32
from common.message_pb2 import *

T = TypeVar('T')

def parseDelimited(data: Any, cls: Type[T]) -> tuple[Type[T], int]:
    try:
        (message_size, pos) = _DecodeVarint32(data, 0)
    except:
        return None, 0

    try:
        current_message = data[pos:(pos + message_size)]
    except IndexError:
        return None, 0
    
    message = cls()
    try:
        message.ParseFromString(current_message)
    except:
        raise ValueError("Wrong data")
    
    pos += message_size
    return message, pos 
