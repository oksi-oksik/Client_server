from common.DelimitedMessagesStreamParser import DelimitedMessagesStreamParser
from common.message_pb2 import *

from google.protobuf.internal.encoder import _VarintBytes

import unittest

class ParserTest(unittest.TestCase):
    def test_oneFastRequest(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)

        message = WrapperMessage(
            request_for_fast_response=RequestForFastResponse()
        )

        data = _VarintBytes(message.ByteSize()) + message.SerializeToString()

        messages = parser.parse(data)
        self.assertEqual(len(messages), 1)

        item = messages.pop()
        self.assertIsInstance(item, WrapperMessage)
        self.assertTrue(item.HasField('request_for_fast_response'))

    def test_someFastRequests(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)

        message = WrapperMessage(
            request_for_fast_response=RequestForFastResponse()
        )

        data = _VarintBytes(message.ByteSize()) + message.SerializeToString()

        count = 5
        messages = parser.parse(data * count)
        self.assertEqual(len(messages), count)

        for item in messages:
            self.assertIsInstance(item, WrapperMessage)
            self.assertTrue(item.HasField('request_for_fast_response'))

    def test_oneSlowRequests(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)

        message = WrapperMessage(
            request_for_slow_response=RequestForSlowResponse(time_in_seconds_to_sleep=0)
        )

        data = _VarintBytes(message.ByteSize()) + message.SerializeToString()

        messages = parser.parse(data)
        self.assertEqual(len(messages), 1)

        item = messages.pop()
        self.assertIsInstance(item, WrapperMessage)
        self.assertTrue(item.HasField('request_for_slow_response'))
        self.assertEqual(item.request_for_slow_response.time_in_seconds_to_sleep, 0)

    def test_someSlowRequests(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)

        message = WrapperMessage(
            request_for_slow_response=RequestForSlowResponse(time_in_seconds_to_sleep=0)
        )

        data = _VarintBytes(message.ByteSize()) + message.SerializeToString()

        count = 5
        messages = parser.parse(data * count)
        self.assertEqual(len(messages), count)

        for item in messages:
            self.assertIsInstance(item, WrapperMessage)
            self.assertTrue(item.HasField('request_for_slow_response'))
            self.assertEqual(item.request_for_slow_response.time_in_seconds_to_sleep, 0)

    def test_someRequests(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)

        fastRequest = WrapperMessage(
            request_for_fast_response=RequestForFastResponse()
        )

        slowRequest = WrapperMessage(
            request_for_slow_response=RequestForSlowResponse(time_in_seconds_to_sleep=0)
        )

        fReqData = _VarintBytes(fastRequest.ByteSize()) + fastRequest.SerializeToString()
        sReqData = _VarintBytes(slowRequest.ByteSize()) + slowRequest.SerializeToString()

        count = 5
        stream = fReqData * int((count + 1) / 2) + sReqData * int(count / 2)

        messages = parser.parse(stream)
        self.assertEqual(len(messages), count)

        for item in messages:
            self.assertTrue(item.HasField('request_for_fast_response') or item.HasField('request_for_slow_response'))
            if item.HasField('request_for_slow_response'):
                self.assertEqual(item.request_for_slow_response.time_in_seconds_to_sleep, 0)

    def test_oneFastResponse(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)
        
        message = WrapperMessage(
            fast_response=FastResponse(current_date_time="")
        )

        data = _VarintBytes(message.ByteSize()) + message.SerializeToString()
        
        messages = parser.parse(data)
        self.assertEqual(len(messages), 1)

        item = messages.pop()
        self.assertTrue(item.HasField('fast_response'))
        self.assertEqual(item.fast_response.current_date_time, "")

    def test_someFastResponses(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)
        
        message = WrapperMessage(
            fast_response=FastResponse(current_date_time="")
        )

        data = _VarintBytes(message.ByteSize()) + message.SerializeToString()
        
        count = 5
        messages = parser.parse(data * count)
        self.assertEqual(len(messages), count)

        for item in messages:
            self.assertTrue(item.HasField('fast_response'))
            self.assertEqual(item.fast_response.current_date_time, "")

    def test_oneSlowResponse(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)
        
        message = WrapperMessage(
            slow_response=SlowResponse(connected_client_count=0)
        )

        data = _VarintBytes(message.ByteSize()) + message.SerializeToString()
        
        messages = parser.parse(data)
        self.assertEqual(len(messages), 1)

        item = messages.pop()
        self.assertTrue(item.HasField('slow_response'))
        self.assertEqual(item.slow_response.connected_client_count, 0)

    def test_someSlowResponses(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)
        
        message = WrapperMessage(
            slow_response=SlowResponse(connected_client_count=0)
        )

        data = _VarintBytes(message.ByteSize()) + message.SerializeToString()
        
        count = 5
        messages = parser.parse(data * count)
        self.assertEqual(len(messages), count)

        for item in messages:
            self.assertTrue(item.HasField('slow_response'))
            self.assertEqual(item.slow_response.connected_client_count, 0)

    def test_someResponses(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)

        fastResponse = WrapperMessage(
            fast_response=FastResponse(current_date_time="")
        )

        slowResponse = WrapperMessage(
            slow_response=SlowResponse(connected_client_count=0)
        )

        fResData = _VarintBytes(fastResponse.ByteSize()) + fastResponse.SerializeToString()
        sResData = _VarintBytes(slowResponse.ByteSize()) + slowResponse.SerializeToString()

        count = 5
        stream = fResData * int((count + 1) / 2) + sResData * int(count / 2)

        messages = parser.parse(stream)
        self.assertEqual(len(messages), count)

        for item in messages:
            self.assertTrue(item.HasField('fast_response') or item.HasField('slow_response'))
            if item.HasField('fast_response'):
                self.assertEqual(item.fast_response.current_date_time, "")
            if item.HasField('slow_response'):
                self.assertEqual(item.slow_response.connected_client_count, 0)

    def test_nullData(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)
        
        messages = parser.parse(None)
        self.assertListEqual(messages, [])

    def test_emptyData(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)
        
        messages = parser.parse("")
        self.assertListEqual(messages, [])

    def test_wrongData(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)
        with self.assertRaises(ValueError):
            parser.parse(b'\x05wrong')

    def test_corruptedData(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)

        message = WrapperMessage(
            fast_response=FastResponse(current_date_time="0")
        )

        data = _VarintBytes(message.ByteSize()) + message.SerializeToString()

        count = 3
        stream = data * count

        corrupted = stream[:len(data)]
        corrupted += b'\x03'
        corrupted += stream[len(data) + 1:]
        with self.assertRaises(ValueError):
            parser.parse(corrupted)
