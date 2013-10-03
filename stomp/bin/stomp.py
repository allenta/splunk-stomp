# -*- coding: utf-8 -*-

"""
:copyright: (c) 2013 by the Allenta Team, see AUTHORS.txt for more details.
:license: GPL, see LICENSE.txt for more details.
"""

import sys
import platform
import time
import logging
import re
import os
import stomppy
import xml.dom.minidom
import xml.sax.saxutils


# Splunk scheme for introspection.
SCHEME = '''<scheme>
    <title>STOMP</title>
    <description>Listen on a STOMP endpoint for incoming messages in a queue/topic.</description>
    <use_external_validation>true</use_external_validation>
    <streaming_mode>xml</streaming_mode>
    <use_single_instance>false</use_single_instance>
    <endpoint>
        <args>
            <arg name="name">
                <title>STOMP endpoint</title>
                <description>STOMP endpoint including hostname/IP address, port number and destination (e.g. 127.0.0.1:61613/queue/whatever).</description>
                <data_type>string</data_type>
                <required_on_create>true</required_on_create>
                <required_on_edit>true</required_on_edit>
            </arg>
            <arg name="username">
                <title>Username</title>
                <description>Username for authenticated MQM connections.</description>
                <data_type>string</data_type>
                <required_on_create>false</required_on_create>
                <required_on_edit>false</required_on_edit>
            </arg>
            <arg name="password">
                <title>Password</title>
                <description>Password for authenticated MQM connections.</description>
                <data_type>string</data_type>
                <required_on_create>false</required_on_create>
                <required_on_edit>false</required_on_edit>
            </arg>
            <arg name="use_explicit_acks">
                <title>Use explicit ACKs</title>
                <description>If enabled, explicitly ACK incoming messages once consumed by Splunk.</description>
                <data_type>boolean</data_type>
                <required_on_create>false</required_on_create>
                <required_on_edit>false</required_on_edit>
            </arg>
            <arg name="use_persistent_subscription">
                <title>Use a persistent subscription</title>
                <description>If enabled, use persitent topic subscriptions.</description>
                <data_type>boolean</data_type>
                <required_on_create>false</required_on_create>
                <required_on_edit>false</required_on_edit>
            </arg>

            <arg name="subscription_id">
                <title>Subscription id</title>
                <description>Subscription id to be used in MQM connections (defaults to 'splunk-stomp').</description>
                <data_type>string</data_type>
                <required_on_create>false</required_on_create>
                <required_on_edit>false</required_on_edit>
            </arg>
        </args>
    </endpoint>
</scheme>
'''


# Splunk helper class.
class SplunkHelper(object):
    PID = None
    IS_WINDOWS = None

    @classmethod
    def init(cls):
        '''
        General Splunk script initializations.
        '''
        # Sets up logging suitable for Splunk comsumption.
        logging.root
        logging.root.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)

        # Fetch current process PID. Required to implement dirty workarounds
        # due to issues when restarting/stopping Splunk (see is_splunkd_running).
        cls.PID = os.getpid()
        cls.IS_WINDOWS = platform.system().lower() == 'windows'

    @classmethod
    def is_splunkd_running(cls):
        '''
        Due to problems killing modular input scripts when stopping/restarting
        Splunk, a dirty check is provided to stop the scripts if the parent
        splunkd process disappears.
        '''
        if not cls.IS_WINDOWS:
            for pid in (cls.PID, os.getppid()):
                gparent_pid = os.popen('ps -p %d -oppid=' % pid).read().strip()
                if not gparent_pid or int(gparent_pid) == 1:
                    return False
        return True

    @classmethod
    def open_stream(self):
        '''
        See http://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ModInputsStream
        '''
        sys.stdout.write('<stream>')
        sys.stdout.flush()

    @classmethod
    def stream_data(self, data):
        '''
        See http://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ModInputsStream
        '''
        sys.stdout.write('<event unbroken="1"><data>')
        sys.stdout.write(xml.sax.saxutils.escape(data))
        sys.stdout.write('</data><done/></event>\n')
        sys.stdout.flush()

    @classmethod
    def close_stream(self):
        '''
        See http://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ModInputsStream
        '''
        sys.stdout.write('</stream>\n')
        sys.stdout.flush()

    @classmethod
    def print_error(cls, message):
        '''
        Prints XML error data to be consumed by Splunk.
        '''
        sys.stdout.write('<error><message>')
        sys.stdout.write(xml.sax.saxutils.escape(message))
        sys.stdout.write('</message></error>')
        sys.stdout.flush()


# Splunk listener class.
class SplunkListener(object):
    def __init__(self, connection, use_explicit_acks):
        self._connection = connection
        self._use_explicit_acks = use_explicit_acks

    def on_message(self, headers, message):
        try:
            # Handle message.
            SplunkHelper.stream_data(message)
        except Exception as e:
            # NACK message.
            if self._use_explicit_acks:
                self._connection.nack(**{
                    'message-id': headers['message-id'],
                    'subscription': headers['subscription'],
                })

            # Log.
            logging.warning('Got exception while processing STOMP message: %s', e)
        else:
            # ACK message.
            if self._use_explicit_acks:
                self._connection.ack(**{
                    'message-id': headers['message-id'],
                    'subscription': headers['subscription'],
                })

    def on_error(self, headers, message):
        # Log.
        logging.error('Got unexpected STOMP error message: %s', message)


def parse_name(name):
    match = re.\
        compile(r'^(?:stomp://)?(?P<host>[^\:]+)\:(?P<port>\d+)(?P<destination>/.*)$').\
        match(name)
    if match:
        groups = match.groupdict()
        return (
            groups['host'],
            int(groups['port']),
            groups['destination'],
        )
    else:
        return None


def get_validation_data():
    '''
    Read XML validation data passed from Splunk.
    '''
    val_data = {}

    # Read everything from stdin.
    val_str = sys.stdin.read()

    # Parse the validation XML.
    doc = xml.dom.minidom.parseString(val_str)
    root = doc.documentElement

    logging.debug('VALIDATION XML: found items')
    item_node = root.getElementsByTagName('item')[0]
    if item_node:
        logging.debug('VALIDATION XML: found item')

        name = item_node.getAttribute('name')
        val_data['stanza'] = name

        params_node = item_node.getElementsByTagName('param')
        for param in params_node:
            name = param.getAttribute('name')
            logging.debug('VALIDATION XML: found param %s', name)
            if name and param.firstChild and \
               param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                val_data[name] = param.firstChild.data

    # Done!
    return val_data


def get_config():
    '''
    Read XML configuration passed from Splunk.
    '''
    config = {}

    try:
        # Read everything from stdin.
        config_str = sys.stdin.read()

        # Parse the config XML.
        doc = xml.dom.minidom.parseString(config_str)
        root = doc.documentElement
        conf_node = root.getElementsByTagName('configuration')[0]
        if conf_node:
            logging.debug('CONFIG XML: found configuration')
            stanza = conf_node.getElementsByTagName('stanza')[0]
            if stanza:
                stanza_name = stanza.getAttribute("name")
                if stanza_name:
                    logging.debug('CONFIG XML: found stanza ' + stanza_name)
                    config['name'] = stanza_name

                    params = stanza.getElementsByTagName('param')
                    for param in params:
                        param_name = param.getAttribute('name')
                        logging.debug("CONFIG XML: found param '%s'", param_name)
                        if param_name and param.firstChild and \
                           param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                            data = param.firstChild.data
                            config[param_name] = data
                            logging.debug("CONFIG XML: '%s' -> '%s'", param_name, data)
    except Exception, e:
        raise Exception('Error getting Splunk configuration via STDIN: %s' % str(e))

    # No configuration?
    if not config:
        raise Exception('Invalid configuration received from Splunk.')

    # Some basic validation: make sure some keys are present (required).
    for key in ('name',):
        if key not in config:
            raise Exception("Invalid configuration received from Splunk: key '%s' is missing." % key)

    # Done!
    return config


def do_scheme():
    '''
    --scheme
    '''
    sys.stdout.write(SCHEME)


def validate_arguments():
    '''
    --validate-arguments
    '''
    val_data = get_validation_data()

    try:
        # Check stanza format.
        name = parse_name(val_data['stanza'])
        if name:
            # Check MQM reachability.
            connection = stomppy.Connection(
                host_and_ports=[(name[0], name[1])],
                user=val_data.get('username', None),
                passcode=val_data.get('password', None))
            try:
                connection.start()
                connection.connect()
            finally:
                connection.disconnect()
        else:
            raise Exception("Wrong stanza format: '%s'." % val_data['stanza'])
    except Exception, e:
        SplunkHelper.print_error('Invalid configuration specified: %s' % str(e))
        sys.exit(1)


def test():
    '''
    --test
    '''
    sys.stdout.write('No tests available for this schema.')
    sys.exit(1)


def usage():
    sys.stdout.write('Usage: %s [--scheme|--validate-arguments]' % os.path.basename(__file__))
    sys.exit(2)


def run():
    # Fetch configuration.
    config = get_config()
    host, port, destination = parse_name(config['name'])
    username = config.get('username', None)
    password = config.get('password', None)
    use_explicit_acks = config.get('use_explicit_acks', False)
    use_persistent_subscription = config.get('use_persistent_subscription', False)
    subscription_id = config.get('subscription_id', 'splunk-stomp')

    # Connect & listen.
    SplunkHelper.open_stream()
    stopping = False
    while not stopping:
        try:
            # Connect & subscribe.
            connection = stomppy.Connection(host_and_ports=[(host, port)], user=username, passcode=password)
            connection.set_listener('', SplunkListener(connection, use_explicit_acks))
            connection.start()
            connection.connect(wait=True)
            connection.subscribe(**{
                'destination': destination,
                'version': 1.1,
                'ack': 'client' if use_explicit_acks else 'auto',
                'persistent': 'true' if use_persistent_subscription else 'false',
                'id': subscription_id,
            })

            # Periodically check for termination.
            while not stopping:
                # Is Splunk already running?
                if not SplunkHelper.is_splunkd_running():
                    stopping = True
                # Is the STOMP connection still valid?
                elif not connection.is_connected():
                    break
                # Wait for the next check.
                else:
                    time.sleep(1)

            # Avoid reconnection stampede when restarting.
            if not stopping:
                time.sleep(1)
        except Exception as e:
            logging.warning('Got exception while consuming STOMP data: %s', e.message)
        finally:
            try:
                connection.disconnect()
            except:
                pass
    SplunkHelper.close_stream()


if __name__ == '__main__':
    SplunkHelper.init()
    if len(sys.argv) > 1:
        if sys.argv[1] == '--scheme':
            do_scheme()
        elif sys.argv[1] == '--validate-arguments':
            validate_arguments()
        elif sys.argv[1] == '--test':
            test()
        else:
            usage()
    else:
        run()

    sys.exit(0)
