from common.helpers import parseDelimited
from common.message_pb2 import *

from google.protobuf.internal.encoder import _VarintBytes

import unittest

class ParseTest(unittest.TestCase):
    def test_default(self):
        message = WrapperMessage(
            request_for_fast_response=RequestForFastResponse()
        )

        data = _VarintBytes(message.ByteSize()) + message.SerializeToString()

        message, bytesConsumed = parseDelimited(data, WrapperMessage)
        
        self.assertTrue(message.HasField('request_for_fast_response'))
        self.assertEqual(bytesConsumed, len(data))

    def test_nullData(self):
        message, bytesConsumed = parseDelimited(None, WrapperMessage)
        
        self.assertIsNone(message)
        self.assertEqual(bytesConsumed, 0)

    def test_emptyData(self):
        message, bytesConsumed = parseDelimited(b'', WrapperMessage)
        
        self.assertIsNone(message)
        self.assertEqual(bytesConsumed, 0)

    def test_wrongData(self):
        with self.assertRaises(ValueError):
            parseDelimited(b'\x05wrong', WrapperMessage)

    def test_corruptedData(self):
        message = WrapperMessage(
            request_for_fast_response=RequestForFastResponse()
        )

        data = _VarintBytes(message.ByteSize()) + message.SerializeToString()

        arr = bytearray(data)
        arr[0] -= 1
        data = bytes(arr)

        with self.assertRaises(ValueError):
            parseDelimited(data, WrapperMessage)