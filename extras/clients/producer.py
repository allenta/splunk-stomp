# -*- coding: utf-8 -*-

from __future__ import absolute_import
from optparse import OptionParser
import stomp


def produce(options):
    connection = stomp.Connection(host_and_ports=[(options.host, options.port)])
    try:
        connection.start()
        connection.connect()
        connection.send(options.message, destination=options.destination)
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
        default='/queue/test',
        help='Destination name (defaults to /queue/test)',
        metavar='QUEUE NAME')
    parser.add_option(
        '--message',
        dest='message',
        help='Message contents (required)',
        metavar='MESSAGE')

    (options, args) = parser.parse_args()
    if options.message:
        produce(options)
    else:
        parser.print_help()
