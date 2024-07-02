from google.protobuf.message import DecodeError
from twisted.internet import reactor, protocol
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ServerFactory as ServFactory
from twisted.internet.endpoints import TCP4ServerEndpoint
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32
import datetime
import logging
import configparser
from common.message_pb2 import *
from common.DelimitedMessagesStreamParser import *


class Server(Protocol):
    def __init__(self, users):
        self.users = users

    def connectionMade(self):
        d = self.transport.getPeer()
        logging.info('Connection from {}\n'.format((d.host, d.port)))
        self.users.append(self)

    def dataReceived(self, data):
        for user in self.users:
            parser = DelimitedMessagesStreamParser(WrapperMessage)
            messages = parser.parse(data)
            if messages:
                for message in messages:
                    if type(message) == WrapperMessage:
                        if message.HasField('slow_response') or message.HasField('fast_response'):
                            self.transport.loseConnection()
                            break
                    else:
                        self.transport.loseConnection()
                        break

                    if message.HasField('request_for_slow_response'):
                        sec = int(message.request_for_slow_response.time_in_seconds_to_sleep)
                        reactor.callLater(sec, self.wake_up)
                    elif message.HasField('request_for_fast_response'):
                        response = WrapperMessage()
                        s = str(datetime.datetime.now().isoformat()).replace('-', '')
                        s = s.replace(':', '')
                        response.fast_response.current_date_time = s
                        self.transport.write(_VarintBytes(response.ByteSize()) + response.SerializeToString())
                        self.transport.loseConnection()
            else:
                self.transport.loseConnection()

    def wake_up(self):
        response = WrapperMessage()
        response.slow_response.connected_client_count = len(self.users)
        self.transport.write(_VarintBytes(response.ByteSize()) + response.SerializeToString())
        self.transport.loseConnection()

    # Событие connectionLost срабатывает при разрыве соединения с клиентом
    def connectionLost(self, reason):
        self.users.remove(self)
        d = self.transport.getPeer()
        logging.info('Close connection from {}\n'.format((d.host, d.port)))

class ServerFactory(ServFactory):
    def __init__(self):
        self.users = []

    def buildProtocol(self, addr):
        return Server(self.users)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename="./logs_twisted.log", filemode="w", format="%(asctime)s %(levelname)s %(message)s")
    config = configparser.ConfigParser()
    config.read('config.ini')

    try:
        port= int(config['DATA']['port'])
        endpoint = TCP4ServerEndpoint(reactor, port)
        endpoint.listen(ServerFactory())
        reactor.run()
    except KeyError:
        logging.error("No 'port' setting in configuration file.")
