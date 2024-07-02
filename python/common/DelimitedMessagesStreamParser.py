from common.helpers import parseDelimited
from typing import TypeVar, Type

T = TypeVar('T')

class DelimitedMessagesStreamParser:
    def __init__(self, cls: Type[T]) -> None:
        self.cls = cls

    def parse(self, data: bytes) -> list[Type[T]]:
        messages = []
        while (data):
            (message, pos) = parseDelimited(data, self.cls)
            if message:
                messages.append(message)
            else:
                return messages
            data = data[pos:]
        return messages

