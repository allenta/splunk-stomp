# -*- coding: utf-8 -*-

from __future__ import absolute_import
from optparse import OptionParser
import time
import stomp


class SimpleListener(object):
    def on_error(self, headers, message):
        print '=> Received an error: %s' % message

    def on_message(self, headers, message):
        print '=> Received a message: %s' % message


def consume(options):
    connection = stomp.Connection(host_and_ports=[(options.host, options.port)])
    try:
        connection.set_listener('', SimpleListener())
        connection.start()
        connection.connect()
        connection.subscribe(destination=options.destination, ack='auto')
        while True:
            time.sleep(60)
    finally:
        connection.disconnect()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
        '--host',
        dest='host',
        default='localhost',
        help='Queue server host (defaults to localhost)',
        metavar='HOST')
    parser.add_option(
        '--port',
        dest='port',
        default=61613,
        type='int',
        help='Queue server host (defaults to 61613)',
        metavar='POST')
    parser.add_option(
        '--destination',
        dest='destination',
        default='/queue/whatever',
        help='Destination name (defaults to /queue/whatever)',
        metavar='QUEUE NAME')

    (options, args) = parser.parse_args()
    consume(options)
